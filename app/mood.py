MOODS = {
    "happy": "😊 Happy",
    "okay": "😐 Okay",
    "sad": "😔 Sad",
    "angry": "😡 Angry",
    "anxious": "😰 Anxious",
    "tired": "😴 Tired",
    "overwhelmed": "😖 Overwhelmed",
}

# moods that should show a gentle prompt to talk more, not just log silently
HEAVY_MOODS = {"sad", "angry", "anxious", "overwhelmed"}

from datetime import datetime, timedelta
from app.models import MoodCheckIn


def calculate_streak(user_id):
    entries = MoodCheckIn.query.filter_by(user_id=user_id).all()
    date_set = {e.created_at.date() for e in entries}
    if not date_set:
        return 0

    streak = 0
    day = datetime.utcnow().date()
    while day in date_set:
        streak += 1
        day -= timedelta(days=1)
    return streak