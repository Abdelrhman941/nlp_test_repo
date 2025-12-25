import json
import pickle
from pathlib import Path
import faiss            # type: ignore
import numpy as np      # type: ignore
from sentence_transformers import SentenceTransformer   # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"

with open(DATA_DIR / "articles_data.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

embedder = SentenceTransformer("all-MiniLM-L6-v2")
documents = []

SIM_THRESHOLD = 0.75
MIN_CHARS = 200

for title, data in articles.items():
    paragraphs = [p.strip() for p in data["text"].split("\n\n") if len(p.strip()) > 50]
    if not paragraphs:
        continue

    embeddings = embedder.encode(paragraphs)
    current_chunk = paragraphs[0]
    current_emb = embeddings[0].reshape(1, -1)
    merged_chunks = []

    for i in range(1, len(paragraphs)):
        sim = cosine_similarity(current_emb, embeddings[i].reshape(1, -1))[0][0]
        if sim >= SIM_THRESHOLD:
            current_chunk += " " + paragraphs[i]
            current_emb = embedder.encode([current_chunk])
        else:
            if len(current_chunk) >= MIN_CHARS:
                merged_chunks.append(current_chunk)
            current_chunk = paragraphs[i]
            current_emb = embeddings[i].reshape(1, -1)

    if len(current_chunk) >= MIN_CHARS:
        merged_chunks.append(current_chunk)

    for chunk in merged_chunks:
        documents.append({
            "text": chunk,
            "metadata": {
                "title": title,
                "url": data["url"],
                "animals": data["animals"],
                "categories": data["categories"]
            }
        })

texts = [d["text"] for d in documents]
embeddings = embedder.encode(texts)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

faiss.write_index(index, str(DATA_DIR / "petmd.index"))
with open(DATA_DIR / "documents_semantic.pkl", "wb") as f:
    pickle.dump(documents, f)

print("FAISS index built.")
