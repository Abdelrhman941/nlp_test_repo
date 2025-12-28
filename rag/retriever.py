# rag/retriever.py

import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache

# ============================================
# Load Resources (once at startup)
# ============================================

print("🔄 Loading retriever...")

embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("./Data/petmd.index")

with open("./Data/documents_semantic.pkl", "rb") as f:
    documents = pickle.load(f)

print(f"✅ Retriever ready! ({len(documents)} documents)")

# ============================================
# Cached Embedding
# ============================================

@lru_cache(maxsize=200)
def get_embedding(text: str) -> tuple:
    """Cache embeddings for repeated queries"""
    return tuple(embedder.encode([text.lower()])[0])

# ============================================
# Main Retrieval Function
# ============================================

def retrieve_chunks(query: str, k: int = 5) -> list:
    """Retrieve top-k relevant chunks"""

    # Get query embedding (cached)
    query_emb = np.array([get_embedding(query)])

    # Search FAISS index
    distances, indices = index.search(query_emb, k)

    # Get documents
    results = []
    for i, idx in enumerate(indices[0]):
        if 0 <= idx < len(documents):
            doc = documents[idx].copy()
            doc["score"] = float(distances[0][i])
            results.append(doc)

    return results
