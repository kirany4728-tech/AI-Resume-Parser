import json
import re
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
#Json_CLeaner
def clean_json_response(text):
    try:
        text = re.sub(r"```json|```", "", text).strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        text = text[start:end]
        return json.loads(text)
    except Exception as e:
        print("JSON Parse Error:", e)
        return None

#parsing of resume:
def parse_resume(text):
    prompt = f"""
You are an experienced HR resume analyzer.

Your task is to carefully read the resume and extract structured data.

Rules:
- Think logically like a human HR recruiter
- Do not guess if information is missing
- If a field is not found return empty string or empty list
- Return ONLY valid JSON
- Do not include explanations

Return JSON in this format:

{{
"full_name": "",
"email": "",
"phone": "",
"location": "",
"key_skills": [],
"designation": "",
"total_experience": "",
"last_company_name": "",
"last_working_date": "",
"education": "",
"age": "",
"industry_category": "",
"domain": ""
}}

Resume Text:
{text}
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional HR resume parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        parsed = clean_json_response(content)

        if parsed is None:
            return {
                "full_name": "",
                "email": "",
                "phone": "",
                "location": "",
                "key_skills": [],
                "designation": "",
                "total_experience": "",
                "last_company_name": "",
                "last_working_date": "",
                "education": "",
                "age": "",
                "industry_category": "",
                "domain": ""
            }

        return parsed

    except Exception as e:
        print("Resume Parse Error:", e)
        return None

#Parse JD:
def parse_jd(jd_text):
    prompt = f"""
You are a senior HR recruiter with strong hiring experience.

Analyze the Job Description carefully and extract structured hiring requirements.

Rules:
- Think like a human recruiter
- Identify mandatory vs preferred skills
- If experience range is not clear return 0
- Return ONLY valid JSON
- No explanations

Return JSON format:

{{
"mandatory_skills": [],
"preferred_skills": [],
"min_exp": 0,
"max_exp": 0,
"designation": "",
"location": "",
"industry_category": "",
"domain": ""
}}

Job Description:
{jd_text}
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert HR job description parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        parsed = clean_json_response(content)

        if parsed is None:
            return {
                "mandatory_skills": [],
                "preferred_skills": [],
                "min_exp": 0,
                "max_exp": 0,
                "designation": "",
                "location": ""
            }

        return parsed

    except Exception as e:
        print("JD Parse Error:", e)
        return None