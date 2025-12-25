from rag.chatbot import rag_chatbot

def main():
    print("Pet Health RAG Chatbot")
    print("=" * 50)
    print("-> Type 'exit' to quit\n")

    while True:
        q = input("You: ").strip()
        if q.lower() == "exit":
            print("Goodbye!")
            break
        if not q:
            continue
        print("Bot:", rag_chatbot(q))
        print()

if __name__ == "__main__":
    main()
