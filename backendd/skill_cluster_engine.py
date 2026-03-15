import re
from sklearn.cluster import KMeans
from embedding_model import model

def clean_skill(skill):

    skill = str(skill).lower()
    skill = re.sub(r"[^a-z0-9#.+ ]", " ", skill)
    skill = re.sub(r"\s+", " ", skill)
    return skill.strip()

def cluster_skills(resume_skills, jd_skills):

    resume_skills = [clean_skill(s) for s in resume_skills]

    jd_skills = [clean_skill(s) for s in jd_skills]
    all_skills = list(set(resume_skills + jd_skills))

    if len(all_skills) < 4:
        return resume_skills
    try:
        embeddings = model.encode(all_skills)
        cluster_count = min(5, len(all_skills))
        kmeans = KMeans(
            n_clusters=cluster_count,
            random_state=42
        )

        labels = kmeans.fit_predict(embeddings)
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(all_skills[i])

        expanded = set(resume_skills)

        for cluster in clusters.values():

            if any(skill in resume_skills for skill in cluster):

                expanded.update(cluster)

        return list(expanded)

    except:

        return resume_skills