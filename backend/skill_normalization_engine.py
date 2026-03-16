import re
def normalize_skill(skill):
    if not skill:
        return ""

    skill = str(skill).lower().strip()
    # remove extra symbols
    skill = re.sub(r"[^a-z0-9+#.\- ]", " ", skill)
    # normalize spaces
    skill = re.sub(r"\s+", " ", skill)

    # normalize common patterns
    skill = skill.replace("js", " javascript")
    skill = skill.replace("node js", "node.js")
    skill = skill.replace("react js", "react")
    skill = skill.replace("next js", "next.js")

    skill = skill.replace("powerbi", "power bi")
    skill = skill.replace("scikit learn", "scikit-learn")
    skill = skill.strip()

    return skill

def normalize_skill_list(skills):

    normalized = []
    for skill in skills:

        cleaned = normalize_skill(skill)

        if cleaned:
            normalized.append(cleaned)

    return list(set(normalized))