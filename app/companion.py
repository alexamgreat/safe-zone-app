import random

GREETINGS = [
    "hey, I'm here. what's on your mind today?",
    "hi there — how are you really doing right now?",
]

RESPONSES = {
    "sad": [
        "that sounds really heavy. do you want to tell me more about what happened?",
        "I'm sorry you're feeling this way. you don't have to carry it alone.",
    ],
    "anxious": [
        "anxiety can feel so overwhelming. what's making you feel this way today?",
        "take a slow breath if you can. what's on your mind?",
    ],
    "angry": [
        "that frustration makes sense. what happened?",
        "it's okay to feel angry. want to talk through it?",
    ],
    "lonely": [
        "feeling alone is really hard. I'm glad you're here talking to me.",
        "you're not as alone as it feels right now.",
    ],
    "tired": [
        "it sounds like you're running on empty. be gentle with yourself today.",
    ],
    "default": [
        "thank you for sharing that with me. can you tell me a bit more?",
        "I hear you. how long have you been feeling this way?",
        "that makes sense. what do you think would help right now?",
    ],
}

KEYWORD_MAP = {
    "sad": "sad", "cry": "sad", "down": "sad",
    "anxious": "anxious", "worried": "anxious", "nervous": "anxious", "stressed": "anxious",
    "angry": "angry", "mad": "angry", "frustrated": "angry",
    "lonely": "lonely", "alone": "lonely", "no friends": "lonely",
    "tired": "tired", "exhausted": "tired", "can't sleep": "tired",
}


def generate_reply(message):
    lowered = message.lower()
    for keyword, category in KEYWORD_MAP.items():
        if keyword in lowered:
            return random.choice(RESPONSES[category])
    return random.choice(RESPONSES["default"])


def greeting():
    return random.choice(GREETINGS)