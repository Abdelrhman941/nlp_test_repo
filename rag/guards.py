# rag/guards.py

import re

# ============================================
# Keywords
# ============================================

EMERGENCY_KEYWORDS = [
    "seizure", "collapse", "unconscious", "bleeding", "blood",
    "poison", "toxic", "not breathing", "choking", "dying",
    "hit by car", "broken", "swallowed"
]

GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "howdy"]

FAREWELLS = ["ok", "okay", "thanks", "thank you", "bye", "goodbye", "got it"]

INVALID_QUERIES = ["continue", "go on", "tell me more", "yes", "no"]

# ============================================
# Functions
# ============================================

def is_english(text: str) -> bool:
    """Check if text is English - improved version"""
    if not text or len(text.strip()) < 2:
        return False

    text = text.strip()

    # Count English letters vs non-English
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total_alpha = len(re.findall(r'[^\s\d\W]', text)) or 1

    # If mostly English letters, accept it
    ratio = english_chars / max(total_alpha, 1)

    # Accept if >70% English characters
    return ratio > 0.7


def is_emergency(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in EMERGENCY_KEYWORDS)


def is_greeting(query: str) -> bool:
    q = query.lower().strip().rstrip('!.,?')
    return q in GREETINGS or any(q.startswith(g) for g in GREETINGS)


def is_farewell(query: str) -> bool:
    q = query.lower().strip().rstrip('!.,?')
    return q in FAREWELLS


def is_invalid_query(query: str) -> bool:
    q = query.lower().strip()
    return len(q) < 3 or q in INVALID_QUERIES
