from sqlalchemy import Column, Integer, String, Text
from database import Base

class ResumeData(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(String, index=True)

    file_hash = Column(String, unique=True, index=True)

    full_name = Column(String)
    email = Column(String)
    phone = Column(String)
    location = Column(String)

    key_skills = Column(Text)

    designation = Column(String)
    total_experience = Column(String)

    last_company_name = Column(String)
    last_working_date = Column(String)

    education = Column(String)

    age = Column(String)

    industry_category = Column(String)
    domain = Column(String)

    matched_skills = Column(Text)
    missing_skills = Column(Text)

    jd_match_score = Column(Integer)

    rank = Column(Integer)