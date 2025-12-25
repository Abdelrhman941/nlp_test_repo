EMERGENCY_KEYWORDS = [
    "seizure", "collapse", "unconscious",
    "bleeding heavily", "poison", "toxic",
    "difficulty breathing", "not breathing"
]

SMALL_TALK = ["hi", "hello", "hey", "thanks", "thank you"]
INVALID_QUERIES = ["continue", "go on", "tell me more"]

def is_emergency(q):
    return any(k in q.lower() for k in EMERGENCY_KEYWORDS)

def is_small_talk(q):
    return q.lower().strip() in SMALL_TALK

def is_invalid_query(q):
    return q.lower().strip() in INVALID_QUERIES
