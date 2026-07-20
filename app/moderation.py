# A simple keyword-based filter. This is intentionally basic to start —
# it catches the most obvious harmful language before anything more
# sophisticated (like a toxicity-detection API) gets added later.

BLOCKED_PHRASES = [
    "shut up", "stupid", "idiot", "dumb", "pathetic", "loser",
    "worthless", "hate you", "kys", "kill yourself", "no one cares",
    "get over it", "just get over it", "so annoying",
]


def is_supportive(text):
    """Returns (True, None) if text passes, or (False, reason) if blocked."""
    lowered = text.lower()
    for phrase in BLOCKED_PHRASES:
        if phrase in lowered:
            return False, "that language isn't allowed here — try rephrasing with kindness."
    return True, None

def is_valid_nickname(name):
    """Returns (True, None) if valid, or (False, reason) if not."""
    name = name.strip()
    if not (2 <= len(name) <= 20):
        return False, "nickname must be between 2 and 20 characters."
    if not all(c.isalnum() or c in " _-" for c in name):
        return False, "nickname can only contain letters, numbers, spaces, - and _."
    lowered = name.lower()
    for phrase in BLOCKED_PHRASES:
        if phrase in lowered:
            return False, "please choose a kinder nickname."
    return True, None

