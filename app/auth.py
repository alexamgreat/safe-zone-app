import random
from flask import session
from app.models import db, User

ADJECTIVES = ["quiet", "gentle", "brave", "calm", "steady", "kind", "hopeful"]
NOUNS = ["maple", "river", "sparrow", "harbor", "meadow", "willow", "compass"]


def generate_username():
    return f"{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}"


def get_or_create_user():
    user_id = session.get("user_id")

    if user_id:
        user = User.query.get(user_id)
        if user:
            return user

    username = generate_username()
    while User.query.filter_by(username=username).first():
        username = generate_username()

    user = User(username=username)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return user