import os
from dotenv import load_dotenv

load_dotenv()

# Resolve the project root (one level above this file's directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config(object):
    """Base Config Object"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Som3$ec5etK*yF0rDr1ftD4ter!')

    # Guard: refuse to start in production with the insecure default key.
    # Set FLASK_ENV=development in your local .env to bypass this check.
    _flask_env = os.environ.get('FLASK_ENV', 'production')
    if _flask_env != 'development' and SECRET_KEY == 'Som3$ec5etK*yF0rDr1ftD4ter!':
        raise ValueError(
            "SECRET_KEY must be set via the SECRET_KEY environment variable in "
            "production. The hardcoded default key must never be used outside of "
            "local development. Set FLASK_ENV=development to bypass this check."
        )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///driftdater.db'
    ).replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Always resolve uploads relative to the project root, not cwd
    _upload_env = os.environ.get('UPLOAD_FOLDER', 'uploads')
    UPLOAD_FOLDER = _upload_env if os.path.isabs(_upload_env) \
                    else os.path.join(BASE_DIR, _upload_env)

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    JWT_EXPIRY_HOURS = int(os.environ.get('JWT_EXPIRY_HOURS', 24))
    WTF_CSRF_ENABLED = False  # CSRF handled via JWT; disable for API

    # Cloudinary — cloud storage for user-uploaded photos
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY    = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

    # CORS — comma-separated list of allowed origins.
    # Defaults to '*' (all) for local dev; restrict to your domain in production.
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')