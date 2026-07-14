import random
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
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


def create_account(user, email, password):
    """Attaches login credentials to the CURRENT anonymous identity.
    Username and history stay exactly the same — this only adds a way
    to get back to this same identity from another device."""
    if User.query.filter_by(email=email).first():
        return False, "that email is already linked to an account."

    user.email = email
    user.password_hash = generate_password_hash(password)
    db.session.commit()
    return True, None


def login_with_email(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash:
        return None, "no account found with that email."
    if not check_password_hash(user.password_hash, password):
        return None, "incorrect password."

    session["user_id"] = user.id
    return user, None
