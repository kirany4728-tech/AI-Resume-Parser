import re
from sklearn.metrics.pairwise import cosine_similarity
from embedding_model import model

def clean_skill(skill):

    skill = str(skill).lower()

    skill = re.sub(r"[^a-z0-9#.+ ]", " ", skill)

    skill = re.sub(r"\s+", " ", skill)
    return skill.strip()

def expand_skills_with_ecosystem(resume_skills, jd_skills=None):

    """
    Automatically detect ecosystem relationships
    Example:
    React → Redux, Next.js
    Python → Django, Flask
    .NET → ASP.NET, Entity Framework
    """

    if not resume_skills:
        return resume_skills

    resume_skills = [clean_skill(s) for s in resume_skills]

    if jd_skills:
        jd_skills = [clean_skill(s) for s in jd_skills]
    else:
        jd_skills = []

    all_skills = list(set(resume_skills + jd_skills))

    if len(all_skills) < 2:
        return resume_skills

    try:

        embeddings = model.encode(all_skills)

        similarity_matrix = cosine_similarity(embeddings)

        expanded = set(resume_skills)

        resume_index = [all_skills.index(s) for s in resume_skills]

        for i in resume_index:

            for j, other_skill in enumerate(all_skills):

                if i == j:
                    continue

                score = similarity_matrix[i][j]

                # ecosystem relation threshold
                if score > 0.68:
                    expanded.add(other_skill)

        return list(expanded)

    except:

        return resume_skills

