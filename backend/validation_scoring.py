import re
from sklearn.metrics.pairwise import cosine_similarity
from skill_ecosystem_ai import expand_skills_with_ecosystem
from skill_intelligence_engine import build_skill_intelligence
from embedding_model import get_embedding


# TEXT CLEANING
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s#.+]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_embeddings_batch(text_list):
    return [get_embedding(text) for text in text_list]


# primary skill matc
def primary_skill_match(resume_skills, jd_skills):

    if not jd_skills:
        return 0, [], []

    resume_skills = list(set([clean_text(s) for s in resume_skills]))
    jd_skills = list(set([clean_text(s) for s in jd_skills]))

    all_texts = resume_skills + jd_skills
    embeddings = get_embeddings_batch(all_texts)

    resume_emb = embeddings[:len(resume_skills)]
    jd_emb = embeddings[len(resume_skills):]

    sim_matrix = cosine_similarity(jd_emb, resume_emb)

    matched = set()
    missing = set()

    for i, jd_skill in enumerate(jd_skills):

        best_score = max(sim_matrix[i])

        if best_score > 0.65:
            matched.add(jd_skill)
        else:
            missing.add(jd_skill)

    score = (len(matched) / len(jd_skills)) * 60

    return int(score), list(matched), list(missing)


#for addi skill match
def additional_skill_match(resume_skills, additional_skills):

    if not additional_skills:
        return 0, []

    resume_skills = [clean_text(s) for s in resume_skills]
    additional_skills = [clean_text(s) for s in additional_skills]

    all_texts = resume_skills + additional_skills
    embeddings = get_embeddings_batch(all_texts)

    resume_emb = embeddings[:len(resume_skills)]
    add_emb = embeddings[len(resume_skills):]

    sim_matrix = cosine_similarity(add_emb, resume_emb)

    matched_secondary = []

    for i in range(len(additional_skills)):
        if max(sim_matrix[i]) > 0.65:
            matched_secondary.append(additional_skills[i])

    score = (len(matched_secondary) / len(additional_skills)) * 5

    return int(score), matched_secondary


# exp. scre
def experience_score(candidate_exp, jd_min, jd_max):

    try:
        candidate_exp = float(re.findall(r"\d+", str(candidate_exp))[0])
        jd_min = float(jd_min) if jd_min else None
        jd_max = float(jd_max) if jd_max else None
    except:
        return 0

    if jd_min and jd_max:

        if jd_min <= candidate_exp <= jd_max:
            return 25

        elif candidate_exp < jd_min:
            ratio = candidate_exp / jd_min
            return int(25 * ratio)

        else:
            diff = candidate_exp - jd_max

            if diff <= 2:
                return 23
            elif diff <= 5:
                return 20
            else:
                return 16

    elif jd_min:
        ratio = candidate_exp / jd_min
        return int(min(25, 25 * ratio))

    else:
        return 15

#semntic match
def semantic_match(resume_text, jd_text):

    resume_text = clean_text(resume_text)[:2000]
    jd_text = clean_text(jd_text)[:2000]

    emb = get_embeddings_batch([resume_text, jd_text])

    sim = cosine_similarity([emb[0]], [emb[1]])[0][0]

    return int(sim * 8)


# designation
def designation_score(candidate_title, jd_title):

    if not candidate_title or not jd_title:
        return 0

    emb = get_embeddings_batch([candidate_title, jd_title])

    sim = cosine_similarity([emb[0]], [emb[1]])[0][0]

    return int(sim * 4)


# LOCATION MATCH
def location_score(candidate_location, jd_location):

    if not candidate_location or not jd_location:
        return 0

    if candidate_location.lower() == jd_location.lower():
        return 3
    return 1


#final score
def calculate_final_score(resume_data, jd_data):

    resume_skills = resume_data.get("skills", [])
    jd_primary_skills = jd_data.get("mandatory_skills", [])
    jd_additional_skills = jd_data.get("additional_skills", [])

    resume_skills = [clean_text(s) for s in resume_skills]
    jd_primary_skills = [clean_text(s) for s in jd_primary_skills]
    jd_additional_skills = [clean_text(s) for s in jd_additional_skills]

    original_resume_skills = list(resume_skills)

    #SKILL EXPANSION
    ai_resume_skills = build_skill_intelligence(
        resume_skills,
        jd_primary_skills
    )

    ai_resume_skills = expand_skills_with_ecosystem(
        ai_resume_skills,
        jd_primary_skills
    )

    ai_resume_skills = list(set(ai_resume_skills))

    resume_text = resume_data.get("resume_text", "")
    resume_exp = resume_data.get("experience", 0)
    resume_title = resume_data.get("designation", "")
    candidate_location = resume_data.get("location", "")

    jd_text = jd_data.get("jd_text", "")
    jd_min = jd_data.get("min_exp", None)
    jd_max = jd_data.get("max_exp", None)
    jd_title = jd_data.get("designation", "")
    jd_location = jd_data.get("location", "")

    primary_score, matched_primary, missing_primary = primary_skill_match(
        ai_resume_skills,
        jd_primary_skills
    )

    additional_score, matched_secondary = additional_skill_match(
        ai_resume_skills,
        jd_additional_skills
    )

    matched_skills = list(set(matched_primary + matched_secondary))
    missing_skills = missing_primary

    exp_score = experience_score(resume_exp, jd_min, jd_max)
    semantic_score = semantic_match(resume_text, jd_text)
    role_score = designation_score(resume_title, jd_title)
    loc_score = location_score(candidate_location, jd_location)

    total_score = (
        primary_score +
        additional_score +
        exp_score +
        semantic_score +
        role_score +
        loc_score
    )

    total_score = min(total_score, 100)

    explanation = f"""
Matched Skills: {', '.join(matched_skills)}
Missing Primary Skills: {', '.join(missing_skills)}

Primary Skill Score: {primary_score}
Additional Skill Score: {additional_score}
Experience Score: {exp_score}
Semantic Score: {semantic_score}
Role Score: {role_score}
Location Score: {loc_score}
"""

    return {
        "final_score": int(total_score),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "explanation": explanation
    }