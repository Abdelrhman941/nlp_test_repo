import json
import time
import random
import re
from typing import List, Dict
from collections import Counter

# RAG imports
from rag.chatbot import rag_chatbot
from rag.retriever import retrieve_chunks

# ML imports
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


# ============================================
# 1️⃣ Load Articles Data
# ============================================

def load_articles(path: str = "./Data/articles_data.json") -> Dict:
    """Load articles from JSON file"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"📚 Loaded {len(data)} articles")
        return data
    except FileNotFoundError:
        print(f"❌ Error: {path} not found!")
        return {}


# ============================================
# 2️⃣ Question Templates
# ============================================

QUESTION_TEMPLATES = [
    # Health
    ("What health issues do {title} have?", "health"),
    ("What diseases are common in {title}?", "health"),
    ("Are {title} prone to any health problems?", "health"),

    # Grooming
    ("How do I groom a {title}?", "grooming"),
    ("What grooming does a {title} need?", "grooming"),

    # Feeding
    ("What should I feed my {title}?", "feeding"),
    ("How often should I feed a {title}?", "feeding"),

    # Size
    ("How big do {title} get?", "size"),
    ("What is the size of a {title}?", "size"),

    # Temperament
    ("What is the temperament of a {title}?", "temperament"),
    ("Are {title} good family pets?", "temperament"),
    ("Are {title} friendly?", "temperament"),

    # Exercise
    ("How much exercise does a {title} need?", "exercise"),
    ("Are {title} active dogs?", "exercise"),

    # General
    ("Tell me about {title}", "general"),
    ("What should I know about {title}?", "general"),
]


# ============================================
# 3️⃣ Auto Extract Keywords
# ============================================

def extract_keywords(text: str, category: str = None, top_n: int = 8) -> List[str]:
    """Extract keywords from text using TF-IDF or patterns"""

    text_lower = text.lower()

    # Category-specific patterns
    patterns = {
    "health": r'\b(?:disease|health|condition|symptom|treatment|infection|dysplasia|allerg|cancer|hip|eye|ear|heart|skin)\w*\b',
    "grooming": r'\b(?:groom|brush|coat|fur|hair|skin|bath|nail|ear|teeth|clean|shed)\w*\b',
    "feeding": r'\b(?:feed|food|diet|eat|nutrition|meal|protein|weight|calorie|portion)\w*\b',
    "size": r'\b(?:\d+[-\s]?\d*\s*(?:inch|pound|lb|kg|cm)|small|medium|large|tall|height|weigh)\w*\b',
    "temperament": r'\b(?:temperament|personality|friendly|loyal|intelligent|smart|playful|affectionate|energetic|gentle|calm|active)\w*\b',
    "exercise": r'\b(?:exercise|active|walk|run|play|energy|activity|minute|hour|daily)\w*\b',
    }


    # Try category pattern first
    if category and category in patterns:
        matches = re.findall(patterns[category], text_lower)
        if matches:
            return list(set(matches))[:top_n]

    # Fallback: TF-IDF
    try:
        sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 20]
        if len(sentences) >= 2:
            vectorizer = TfidfVectorizer(max_features=30, stop_words='english')
            tfidf = vectorizer.fit_transform(sentences)
            features = vectorizer.get_feature_names_out()
            scores = np.array(tfidf.sum(axis=0)).flatten()
            top_idx = scores.argsort()[-top_n:][::-1]
            return [features[i] for i in top_idx]
    except:
        pass

    # Final fallback: word frequency
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text_lower)
    stopwords = {'that', 'this', 'with', 'from', 'have', 'they', 'their', 'will', 'would',
                 'could', 'should', 'also', 'been', 'were', 'being', 'which', 'these'}
    words = [w for w in words if w not in stopwords]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]


# ============================================
# 4️⃣ Generate Test Cases Automatically
# ============================================

def generate_test_cases(articles: Dict, num_per_article: int = 2) -> List[Dict]:
    """Auto-generate test cases from articles"""

    test_cases = []

    for title, data in articles.items():
        text = data.get("text", "")

        # Skip short articles
        if len(text) < 200:
            continue

        # Select random templates
        templates = random.sample(
            QUESTION_TEMPLATES,
            min(num_per_article, len(QUESTION_TEMPLATES))
        )

        for template, category in templates:
            question = template.format(title=title)
            keywords = extract_keywords(text, category)

            test_cases.append({
                "question": question,
                "expected_source": title,
                "keywords": keywords,
                "category": category
            })

    return test_cases


# ============================================
# 5️⃣ Evaluator Class
# ============================================

class Evaluator:
    """Simple RAG Evaluator"""

    def __init__(self):
        print("🔄 Loading evaluator...")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Evaluator ready!")

    def semantic_score(self, question: str, response: str) -> float:
        """Semantic similarity between question and response"""
        emb = self.embedder.encode([question, response])
        sim = cosine_similarity([emb[0]], [emb[1]])[0][0]
        return max(0, float(sim))

    def keyword_score(self, response: str, keywords: List[str]) -> float:
        """Percentage of keywords found in response"""
        if not keywords:
            return 1.0
        response_lower = response.lower()
        found = sum(1 for kw in keywords if kw.lower() in response_lower)
        return found / len(keywords)

    def source_found(self, chunks: List[Dict], expected: str) -> bool:
        """Check if expected source was retrieved"""
        if not expected:
            return True
        for chunk in chunks:
            title = chunk.get("metadata", {}).get("title", "")
            if expected.lower() in title.lower():
                return True
        return False

    def retrieval_quality(self, question: str, chunks: List[Dict]) -> float:
        """Average relevance of retrieved chunks"""
        if not chunks:
            return 0.0

        q_emb = self.embedder.encode([question])[0]
        scores = []

        for chunk in chunks:
            c_emb = self.embedder.encode([chunk["text"]])[0]
            sim = cosine_similarity([q_emb], [c_emb])[0][0]
            scores.append(float(sim))

        return np.mean(scores)


# ============================================
# 6️⃣ Main Evaluation Function
# ============================================

def run_evaluation(num_tests: int = 30, questions_per_article: int = 2, verbose: bool = True):
    """Run full evaluation"""

    print("\n" + "=" * 60)
    print("🐾 PET HEALTH RAG - EVALUATION")
    print("=" * 60)

    # Load articles
    articles = load_articles()
    if not articles:
        return None

    # Generate test cases
    print("🔧 Generating test cases...")
    all_tests = generate_test_cases(articles, questions_per_article)
    print(f"   Generated {len(all_tests)} possible tests")

    # Sample tests
    if len(all_tests) > num_tests:
        test_cases = random.sample(all_tests, num_tests)
    else:
        test_cases = all_tests

    print(f"🧪 Running {len(test_cases)} tests...\n")

    # Initialize
    evaluator = Evaluator()

    # Results storage
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "scores": {
            "semantic": [],
            "keyword": [],
            "retrieval": [],
            "response_time": []
        },
        "by_category": {},
        "details": []
    }

    # Run tests
    for i, test in enumerate(test_cases, 1):
        question = test["question"]
        keywords = test["keywords"]
        expected = test["expected_source"]
        category = test["category"]

        if verbose:
            print(f"[{i:02d}/{len(test_cases)}] {category}: {question[:45]}...")

        # Time the response
        start = time.time()
        response = rag_chatbot(question)
        elapsed = time.time() - start

        # Get chunks
        chunks = retrieve_chunks(question, k=5)

        # Calculate scores
        sem_score = evaluator.semantic_score(question, response)
        kw_score = evaluator.keyword_score(response, keywords)
        ret_score = evaluator.retrieval_quality(question, chunks)
        src_found = evaluator.source_found(chunks, expected)

        # Store scores
        results["scores"]["semantic"].append(sem_score)
        results["scores"]["keyword"].append(kw_score)
        results["scores"]["retrieval"].append(ret_score)
        results["scores"]["response_time"].append(elapsed)

        # Pass/Fail criteria
        passed = bool(
            (sem_score >= 0.25)
            and src_found
            and (kw_score >= 0.2 or ret_score >= 0.3)
            )


        # Update category stats
        if category not in results["by_category"]:
            results["by_category"][category] = {"passed": 0, "failed": 0}

        if passed:
            results["passed"] += 1
            results["by_category"][category]["passed"] += 1
            status = "✅"
        else:
            results["failed"] += 1
            results["by_category"][category]["failed"] += 1
            status = "❌"

        # Store details
        results["details"].append({
            "question": question,
            "category": category,
            "expected_source": expected,
            "response": response[:300],
            "scores": {
                "semantic": round(sem_score, 3),
                "keyword": round(kw_score, 3),
                "retrieval": round(ret_score, 3)
            },
            "source_found": src_found,
            "time": round(elapsed, 2),
            "passed": passed
        })

        if verbose:
            src_icon = "✓" if src_found else "✗"
            print(f"     {status} sem:{sem_score:.2f} | kw:{kw_score:.2f} | ret:{ret_score:.2f} | src:{src_icon} | {elapsed:.1f}s")

    # Print summary
    print_summary(results)

    # Save results
    save_results(results)

    return results


# ============================================
# 7️⃣ Print Summary
# ============================================

def print_summary(results: Dict):
    """Print evaluation summary"""

    print("\n" + "=" * 60)
    print("📊 EVALUATION RESULTS")
    print("=" * 60)

    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]

    # Averages
    avg_sem = np.mean(results["scores"]["semantic"])
    avg_kw = np.mean(results["scores"]["keyword"])
    avg_ret = np.mean(results["scores"]["retrieval"])
    avg_time = np.mean(results["scores"]["response_time"])

    print(f"""
┌────────────────────────────────────────────────────────────────────┐
│  OVERALL RESULTS                                                   │
├────────────────────────────────────────────────────────────────────┤
│  Total Tests:        {total:>5}                                    │
│  Passed:             {passed:>5}  ({passed/total*100:>5.1f}%)      │
│  Failed:             {failed:>5}  ({failed/total*100:>5.1f}%)      │
├────────────────────────────────────────────────────────────────────┤
│  METRICS                                                           │
├────────────────────────────────────────────────────────────────────┤
│  Avg Semantic Score:   {avg_sem:>6.1%}                             │
│  Avg Keyword Score:    {avg_kw:>6.1%}                              │
│  Avg Retrieval Score:  {avg_ret:>6.1%}                             │
│  Avg Response Time:    {avg_time:>5.2f}s                           │
└────────────────────────────────────────────────────────────────────┘
    """)

    # By category
    print("📈 BY CATEGORY:")
    print("─" * 45)

    for cat, stats in sorted(results["by_category"].items()):
        cat_total = stats["passed"] + stats["failed"]
        pct = stats["passed"] / cat_total * 100 if cat_total > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        print(f"  {cat:<15} {bar} {stats['passed']}/{cat_total} ({pct:.0f}%)")

    print()


# ============================================
# 8️⃣ Save Results
# ============================================

def save_results(results: Dict):
    """Save results to files"""

    # JSON
    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Markdown report
    report = generate_markdown_report(results)
    with open("evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("💾 Saved: evaluation_results.json, evaluation_report.md")


def generate_markdown_report(results: Dict) -> str:
    """Generate markdown report"""

    total = results["total"]
    passed = results["passed"]

    avg_sem = np.mean(results["scores"]["semantic"])
    avg_kw = np.mean(results["scores"]["keyword"])
    avg_ret = np.mean(results["scores"]["retrieval"])
    avg_time = np.mean(results["scores"]["response_time"])

    report = f"""# 🐾 Pet Health RAG - Evaluation Report

## 📊 Summary

| Metric | Value |
|--------|-------|
| Total Tests | {total} |
| Passed | {passed} ({passed/total*100:.1f}%) |
| Failed | {results['failed']} ({results['failed']/total*100:.1f}%) |
| Avg Semantic Score | {avg_sem:.1%} |
| Avg Keyword Score | {avg_kw:.1%} |
| Avg Retrieval Score | {avg_ret:.1%} |
| Avg Response Time | {avg_time:.2f}s |

## 📈 By Category

| Category | Passed | Total | Rate |
|----------|--------|-------|------|
"""

    for cat, stats in sorted(results["by_category"].items()):
        cat_total = stats["passed"] + stats["failed"]
        pct = stats["passed"] / cat_total * 100 if cat_total > 0 else 0
        report += f"| {cat} | {stats['passed']} | {cat_total} | {pct:.0f}% |\n"

    # Failed tests
    failed_tests = [d for d in results["details"] if not d["passed"]]

    if failed_tests:
        report += f"\n## ❌ Failed Tests ({len(failed_tests)})\n\n"
        for t in failed_tests[:10]:  # Max 10
            report += f"""
### {t['category']}: {t['question'][:50]}...
- **Expected Source:** {t['expected_source']}
- **Source Found:** {'Yes' if t['source_found'] else 'No'}
- **Semantic:** {t['scores']['semantic']:.2f}
- **Response:** {t['response'][:150]}...

---
"""

    return report


# ============================================
# 9️⃣ Quick Test
# ============================================

def quick_test(n: int = 5):
    """Quick test for debugging"""
    print("⚡ Quick Test Mode")
    return run_evaluation(num_tests=n, questions_per_article=1, verbose=True)


# ============================================
# 🚀 Main
# ============================================

if __name__ == "__main__":
    import sys

    print("""
╔════════════════════════════════════════════════════════════╗
║         🐾 PET HEALTH RAG - EVALUATION SUITE 🐾           ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Check for command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            quick_test(5)
        elif sys.argv[1] == "--full":
            run_evaluation(num_tests=50, questions_per_article=3)
        elif sys.argv[1].isdigit():
            run_evaluation(num_tests=int(sys.argv[1]))
        else:
            print("Usage: python evaluation.py [--quick | --full | <num_tests>]")
    else:
        # Default: 30 tests
        run_evaluation(num_tests=30, questions_per_article=2)

    print("\n✅ Evaluation complete!")
