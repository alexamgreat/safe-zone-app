# Detects language that may signal a mental health crisis, so we can
# immediately show real resources instead of just posting normally.
# This is intentionally broad (it's fine to over-trigger) — missing a
# real crisis is a much worse outcome than showing resources too often.

CRISIS_PHRASES = [
    "kill myself", "want to die", "end my life", "suicidal",
    "suicide", "hurting myself", "hurt myself", "self harm",
    "self-harm", "cutting myself", "don't want to live",
    "no reason to live", "better off dead", "being abused",
    "he hits me", "she hits me", "they hit me",
]


def check_for_crisis(text):
    """Returns True if the text contains crisis-level language."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in CRISIS_PHRASES)