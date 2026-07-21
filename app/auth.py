import random
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
from app.moderation import is_valid_nickname


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def signup(nickname, password, email=None):
    nickname = nickname.strip()

    ok, reason = is_valid_nickname(nickname)
    if not ok:
        return None, reason

    if User.query.filter_by(username=nickname).first():
        return None, "that nickname is already taken."

    if len(password) < 6:
        return None, "password must be at least 6 characters."

    email = email.strip().lower() if email else None
    if email and User.query.filter_by(email=email).first():
        return None, "that email is already linked to another account."

    user = User(
        username=nickname,
        password_hash=generate_password_hash(password),
        email=email,
    )
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return user, None


def login(nickname, password):
    nickname = nickname.strip()
    user = User.query.filter_by(username=nickname).first()

    if not user or not user.password_hash:
        return None, "no account found with that nickname."
    if not check_password_hash(user.password_hash, password):
        return None, "incorrect password."

    session["user_id"] = user.id
    return user, None


def logout():
    session.pop("user_id", None)


def reset_password(email, new_password):
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return None, "no account found with that email."
    if len(new_password) < 6:
        return None, "password must be at least 6 characters."
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return user, None