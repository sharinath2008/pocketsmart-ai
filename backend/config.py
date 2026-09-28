import os
from dotenv import load_dotenv

load_dotenv()

_IS_PROD = os.getenv("FLASK_ENV", "development") == "production"


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # Frontend (GitHub Pages) origins allowed to call this API.
    # Must be explicit (not "*") because cookies/credentials are enabled.
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
        ).split(",")
        if origin.strip()
    ]

    # Cross-site session cookies (GitHub Pages -> API on another domain)
    # require SameSite=None + Secure, which only works over HTTPS.
    # Locally (plain http) we use Lax so cookies still work.
    SESSION_COOKIE_SAMESITE = "None" if _IS_PROD else "Lax"
    SESSION_COOKIE_SECURE = _IS_PROD

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB upload limit
