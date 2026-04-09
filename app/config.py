import os
from dotenv import load_dotenv

load_dotenv()

# Resolve the project root (one level above this file's directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config(object):
    """Base Config Object"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Som3$ec5etK*yF0rDr1ftD4ter!')
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