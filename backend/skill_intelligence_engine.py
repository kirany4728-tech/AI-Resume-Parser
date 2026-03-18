import re
from sklearn.metrics.pairwise import cosine_similarity
from embedding_model import model
from embedding_model import get_embedding

def clean_skill(skill):

    skill = str(skill).lower()
    skill = re.sub(r"[^a-z0-9#.+ ]", " ", skill)
    skill = re.sub(r"\s+", " ", skill)
    return skill.strip()

def build_skill_intelligence(resume_skills, jd_skills):

    resume_skills = [clean_skill(s) for s in resume_skills]

    jd_skills = [clean_skill(s) for s in jd_skills]

    all_skills = list(set(resume_skills + jd_skills))

    if len(all_skills) < 2:

        return resume_skills

    embeddings = get_embedding(all_skills)

    sim_matrix = cosine_similarity(embeddings)

    expanded = set(resume_skills)

    for i, skill in enumerate(all_skills):

        if skill in resume_skills:

            for j, other_skill in enumerate(all_skills):

                if i == j:
                    continue

                score = sim_matrix[i][j]

                # intelligent relation threshold
                if score > 0.60:

                    expanded.add(other_skill)

    return list(expanded)