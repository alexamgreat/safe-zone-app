import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

# Render provides a DATABASE_URL for a real Postgres database in production.
# Locally, with no DATABASE_URL set, we fall back to SQLite like before.
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    # SQLAlchemy needs "postgresql://" not "postgres://"
    database_url = database_url.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-not-safe")
    SQLALCHEMY_DATABASE_URI = database_url or "sqlite:///" + os.path.join(
        BASE_DIR, "instance", "safezone.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False