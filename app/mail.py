from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for

mail = Mail()


def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generate_reset_token(email):
    return get_serializer().dumps(email, salt="password-reset")


def verify_reset_token(token, max_age=3600):
    """max_age is in seconds — 3600 = link expires after 1 hour."""
    try:
        return get_serializer().loads(token, salt="password-reset", max_age=max_age)
    except Exception:
        return None


def send_reset_email(email, token):
    reset_url = url_for("reset_with_token", token=token, _external=True)
    msg = Message(
        subject="Reset your Safe Zone password",
        recipients=[email],
        body=f"Hi,\n\nClick the link below to reset your Safe Zone password. This link expires in 1 hour.\n\n{reset_url}\n\nIf you didn't request this, you can ignore this email.",
    )
    mail.send(msg)