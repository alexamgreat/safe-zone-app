import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

# Make sure the instance folder exists before SQLite tries to write to it.
os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-not-safe")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR, "instance", "safezone.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False