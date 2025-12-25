import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from rag.retriever import retrieve_chunks
from rag.guards import is_emergency, is_small_talk, is_invalid_query

# استخدم نموذج أصغر بكثير
LLM_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # أو "microsoft/phi-2" حجمه أصغر

tokenizer = AutoTokenizer.from_pretrained(LLM_NAME)
model = AutoModelForCausalLM.from_pretrained(
    LLM_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

def rag_chatbot(question, k=8):
    if is_small_talk(question):
        return "Hello! I can help with questions about pet health and care."

    if is_invalid_query(question):
        return "Please ask a complete and specific question."

    chunks = retrieve_chunks(question, k)
    context = "\n\n".join(c["text"] for c in chunks)

    prefix = ""
    if is_emergency(question):
        prefix = "This may be a medical emergency. Please contact a veterinarian immediately.\n\n"

    prompt = f"""{prefix}
You are a veterinary RAG assistant.

Rules:
- Answer ONLY using the context.
- If the answer is not explicitly stated, reply ONLY:
  "I don't have enough information."

Context:
{context}

Question:
{question}

Answer:
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_new_tokens=150, do_sample=False)
    return tokenizer.decode(output[0], skip_special_tokens=True).split("Answer:")[-1].strip()
