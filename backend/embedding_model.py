from sentence_transformers import SentenceTransformer

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cpu"
)

embedding_cache = {}

def get_embedding(text):

    if isinstance(text, list):
        return [get_embedding(t) for t in text]

    text = str(text).lower().strip()

    if text in embedding_cache:
        return embedding_cache[text]

    emb = model.encode(text)
    embedding_cache[text] = emb

    return emb