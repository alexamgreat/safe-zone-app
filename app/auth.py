import random
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

ADJECTIVES = ["quiet", "gentle", "brave", "calm", "steady", "kind", "hopeful"]
NOUNS = ["maple", "river", "sparrow", "harbor", "meadow", "willow", "compass"]


def generate_username():
    return f"{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}"


def get_current_user():
    """Returns the logged-in user, or None if nobody is logged in.
    Unlike before, this NEVER creates a new user automatically."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def signup(email, password):
    """Creates a brand new anonymous identity AND attaches login
    credentials in one step, since accounts are now required upfront."""
    email = email.strip().lower()

    if User.query.filter_by(email=email).first():
        return None, "that email is already registered."

    username = generate_username()
    while User.query.filter_by(username=username).first():
        username = generate_username()

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return user, None


def login(email, password):
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not user.password_hash:
        return None, "no account found with that email."
    if not check_password_hash(user.password_hash, password):
        return None, "incorrect password."

    session["user_id"] = user.id
    return user, None


def logout():
    session.pop("user_id", None)
