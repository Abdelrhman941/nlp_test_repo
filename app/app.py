from rag.chatbot import rag_chatbot

print("Pet Health RAG Chatbot")
while True:
    q = input("You: ").strip()
    if q.lower() == "exit":
        break
    print("Bot:", rag_chatbot(q))
