import datetime

QUOTES = [
    "The storm will pass and the sun will rise again.",
    "Progress is still progress, no matter how small.",
    "You don't have to be perfect to be worthy.",
    "Asking for help is brave, not weak.",
    "One bad day doesn't define you.",
    "You are stronger than you think.",
]


def quote_of_the_day():
    idx = datetime.date.today().toordinal() % len(QUOTES)
    return QUOTES[idx]