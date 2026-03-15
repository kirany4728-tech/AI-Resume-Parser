import re
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
# Single embedding model (semantic understanding like ATS)
from embedding_model import model

def clean_skill(skill):

    skill = str(skill).lower()
    skill = re.sub(r"[^a-z0-9#.+ ]", " ", skill)
    skill = re.sub(r"\s+", " ", skill)
    return skill.strip()

def build_skill_graph(resume_skills, jd_skills):

    """
    Build dynamic skill relationship graph
    No hardcoded tech stacks.
    """

    skills = list(set(resume_skills + jd_skills))

    if len(skills) < 2:
        return nx.Graph()

    cleaned_skills = [clean_skill(s) for s in skills]

    embeddings = model.encode(cleaned_skills)

    similarity_matrix = cosine_similarity(embeddings)

    graph = nx.Graph()

    for i, skill in enumerate(cleaned_skills):

        graph.add_node(skill)

        for j, other_skill in enumerate(cleaned_skills):

            if i == j:
                continue

            score = similarity_matrix[i][j]

            # semantic relation threshold
            if score > 0.70:

                graph.add_edge(skill, other_skill, weight=score)

    return graph


def expand_skills_graph(resume_skills, jd_skills):

    """
    Expand resume skills using graph neighbors
    """

    graph = build_skill_graph(resume_skills, jd_skills)

    expanded = set()

    for skill in resume_skills:

        skill = clean_skill(skill)

        expanded.add(skill)

        if skill in graph:

            neighbors = list(graph.neighbors(skill))

            for n in neighbors:
                expanded.add(n)

    return list(expanded)