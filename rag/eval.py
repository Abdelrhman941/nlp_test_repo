import pandas as pd
from rag.chatbot import rag_chatbot
from rag.retriever import retrieve_chunks
import time

# 1. قائمة بأسئلة اختبارية (يفضل تكون من الداتا اللي عندك)
test_dataset = [
    {
        "question": "What should I feed my dog?",
        "expected_answer": "High-quality dog food suitable for their age and size."
    },
    {
        "question": "Symptoms of chocolate poisoning in cats",
        "expected_answer": "Vomiting, diarrhea, rapid breathing, and seizures."
    },
    # ضيف هنا 10-20 سؤال من المقالات اللي عملت لها Scraping
]

def evaluate_rag():
    results = []
    print(f"Starting Evaluation on {len(test_dataset)} questions...\n")

    for entry in test_dataset:
        q = entry["question"]
        expected = entry["expected_answer"]

        start_time = time.time()

        # تشغيل الـ Pipeline
        # 1. اختبار الـ Retriever
        retrieved_docs = retrieve_chunks(q, k=3)
        context = " ".join([d["text"] for d in retrieved_docs])

        # 2. اختبار الـ Chatbot
        actual_answer = rag_chatbot(q)

        duration = time.time() - start_time

        # تقييم بسيط (هل الإجابة المتوقعة موجودة في الـ Context؟)
        # ملاحظة: التقييم الاحترافي بيستخدم LLM تاني للتقييم (LLM-as-a-judge)
        results.append({
            "Question": q,
            "Expected": expected,
            "Actual": actual_answer,
            "Latency (s)": round(duration, 2),
            "Context_Length": len(context)
        })
        print(f"Finished: {q[:30]}... ({round(duration, 2)}s)")

    # تحويل النتائج لجدول DataFrame
    df = pd.DataFrame(results)

    # حفظ النتائج في ملف Excel أو CSV للعرض في المشروع
    df.to_csv("evaluation_results.csv", index=False)

    print("\n" + "="*30)
    print("Evaluation Complete!")
    print(f"Average Latency: {df['Latency (s)'].mean():.2f}s")
    print("Results saved to 'evaluation_results.csv'")

if __name__ == "__main__":
    evaluate_rag()
