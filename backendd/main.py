from typing import List
import csv
import io
import os
import json
import hashlib
import logging
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from extractor import extract_text_from_pdf, extract_text_from_docx
from ai_parser import parse_resume, parse_jd

from validation_scoring import calculate_final_score

from database import SessionLocal, engine
from models import ResumeData
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def root():
    return {"message": "AI Resume Parser Backend Running"}


@app.post("/upload/")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    jd_text: str = Form("")
):

    db = SessionLocal()

    batch_id = str(uuid.uuid4())

    parsed = 0
    duplicate = 0
    errors = 0

    jd_data = {}

    if jd_text.strip():
        jd_data = parse_jd(jd_text)
        jd_data["jd_text"] = jd_text

    for file in files:

        try:

            contents = await file.read()

            file_hash = hashlib.md5(contents).hexdigest()

            existing = db.query(ResumeData).filter(
                ResumeData.file_hash == file_hash
            ).first()

            if existing:
                duplicate += 1
                continue

            file_path = os.path.join(UPLOAD_FOLDER, file.filename)

            with open(file_path, "wb") as f:
                f.write(contents)

            if file.filename.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)

            elif file.filename.endswith(".docx"):
                text = extract_text_from_docx(file_path)

            else:
                continue

            result = parse_resume(text)

            if not result:
                errors += 1
                continue

            #Ats  scoringg

            if jd_data:

                resume_data = {

                    "skills": result.get("key_skills", []),
                    "resume_text": text,
                    "experience": result.get("total_experience", 0),
                    "designation": result.get("designation", ""),
                    "projects": [],
                    "location": result.get("location", "")
                }

                score_result = calculate_final_score(
                    resume_data,
                    jd_data
                )
                result["ai_explanation"] = score_result.get("explanation", "")
                result["matched_skills"] = score_result.get("matched_skills", [])
                result["missing_skills"] = score_result.get("missing_skills", [])
                result["jd_match_score"] = score_result.get("final_score", 0)

            else:

                result["matched_skills"] = []
                result["missing_skills"] = []
                result["jd_match_score"] = 0

            education_str = json.dumps(result.get("education", []))

            entry = ResumeData(

                batch_id=batch_id,

                file_hash=file_hash,

                full_name=result.get("full_name"),
                email=result.get("email"),
                phone=result.get("phone"),
                location=result.get("location"),

                key_skills=", ".join(result.get("key_skills", [])),

                designation=result.get("designation"),
                total_experience=result.get("total_experience"),

                last_company_name=result.get("last_company_name"),
                last_working_date=result.get("last_working_date"),

                education=education_str,

                age=result.get("age"),

                industry_category=result.get("industry_category"),
                domain=result.get("domain"),

                matched_skills=", ".join(result.get("matched_skills", [])),
                missing_skills=", ".join(result.get("missing_skills", [])),

                jd_match_score=result.get("jd_match_score", 0)

            )

            db.add(entry)
            db.commit()

            parsed += 1

        except Exception as e:

            errors += 1
            db.rollback()

            logging.error(f"Resume processing failed: {file.filename}")

#RANKING:

    all_data = db.query(ResumeData).filter(
        ResumeData.batch_id == batch_id
    ).all()

    sorted_data = sorted(
        all_data,
        key=lambda x: x.jd_match_score,
        reverse=True
    )

    for i, row in enumerate(sorted_data, start=1):
        row.rank = i

    db.commit()

    output = io.StringIO()
    writer = csv.writer(output)

    headers = ["rank"] + [column.name for column in ResumeData.__table__.columns]

    writer.writerow(headers)

    for row in sorted_data:

        writer.writerow(
            [row.rank] +
            [getattr(row, column.name) for column in ResumeData.__table__.columns]
        )

    output.seek(0)

    db.close()

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=ranked_resumes.csv",
            "X-Parsed": str(parsed),
            "X-Duplicate": str(duplicate),
            "X-Errors": str(errors)
        }
    )