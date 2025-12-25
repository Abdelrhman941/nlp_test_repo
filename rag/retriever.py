import pickle
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"

embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(str(DATA_DIR / "petmd.index"))

with open(DATA_DIR / "documents_semantic.pkl", "rb") as f:
    documents = pickle.load(f)

def retrieve_chunks(query, k=8):
    query_emb = embedder.encode([query.lower()])
    _, I = index.search(np.array(query_emb), k)
    return [documents[i] for i in I[0]]
