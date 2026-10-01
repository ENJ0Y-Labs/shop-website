import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SESSION_TYPE = os.getenv(
        "SESSION_TYPE",
        "redis" if APP_ENV == "production" else "filesystem",
    ).strip().lower()
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv(
        "SESSION_COOKIE_SAMESITE",
        "None" if APP_ENV == "production" else "Lax",
    )
    SESSION_COOKIE_SECURE = os.getenv(
        "SESSION_COOKIE_SECURE",
        "true" if APP_ENV == "production" else "false",
    ).lower() == "true"
    SESSION_COOKIE_NAME = "enj0y_session"

    REDIS_URL = os.getenv("REDIS_URL", "").strip()
    SESSION_FILE_DIR = os.getenv(
        "SESSION_FILE_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".flask_session"),
    )

    FRONTEND_URL = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
    configured_origins = [
        origin.strip().rstrip("/")
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if FRONTEND_URL and FRONTEND_URL not in configured_origins:
        configured_origins.insert(0, FRONTEND_URL)
    CORS_ORIGINS = configured_origins or ["http://localhost:5173"]

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:5000/api/auth/google/callback",
    )

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "product-images")

    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
    MAILGUN_FROM_EMAIL = os.getenv("MAILGUN_FROM_EMAIL")
    MAILGUN_API_BASE_URL = os.getenv("MAILGUN_API_BASE_URL", "https://api.mailgun.net").rstrip("/")
    MAILGUN_TIMEOUT = int(os.getenv("MAILGUN_TIMEOUT", "10"))
