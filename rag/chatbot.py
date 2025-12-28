import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from rag.retriever import retrieve_chunks
from rag.guards import is_emergency, is_greeting, is_farewell, is_invalid_query, is_english

LLM_NAME = "Qwen/Qwen2.5-3B-Instruct" # "Qwen/Qwen2.5-1.5B-Instruct"

print(f"🔄 Loading {LLM_NAME}...")

tokenizer = AutoTokenizer.from_pretrained(LLM_NAME)

# Check for GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"   Device: {device}")

# Load model
if device == "cuda":
    model = AutoModelForCausalLM.from_pretrained(
        LLM_NAME, dtype=torch.float16, device_map="auto", trust_remote_code=True
    )
else:
    # CPU - use smaller precision
    model = AutoModelForCausalLM.from_pretrained(
        LLM_NAME, dtype=torch.float32, trust_remote_code=True, low_cpu_mem_usage=True
    ).to(device)

model.eval()
print("✅ Model loaded!")

def rag_chatbot(question: str, k: int = 5) -> str:
    """Main RAG chatbot function"""

    question = question.strip()

    # Guard checks
    if not is_english(question):
        return "🌐 Sorry, I only support English at the moment. Please ask your question in English!"

    if is_greeting(question):
        return "👋 Hello! I'm your Pet Health Assistant. How can I help you with your furry friend today?"

    if is_farewell(question):
        return "😊 You're welcome! Feel free to ask if you have more questions. Take care! 🐾"

    if is_invalid_query(question):
        return "🤔 Could you please ask a more specific question about your pet's health?"

    # Retrieve context
    chunks = retrieve_chunks(question, k=k)

    if not chunks:
        return "😕 I couldn't find relevant information. Please try a different question."

    context = "\n\n".join(c["text"][:500] for c in chunks[:3])  # Limit context size

    # Emergency check
    prefix = ""
    if is_emergency(question):
        prefix = "🚨 **EMERGENCY:** Please contact a veterinarian immediately!\n\n"

    # Build prompt (shorter for speed)
    prompt = f"""Answer the question using ONLY the context. Be brief and helpful.

Context:
{context}

Question: {question}

Answer:"""

    # Generate
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,  # Shorter for speed
            do_sample=False,     # Greedy = faster
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = response.split("Answer:")[-1].strip()

    # Clean up
    if not answer or len(answer) < 10:
        answer = "I don't have specific information about that. Please consult a veterinarian."

    return prefix + answer
