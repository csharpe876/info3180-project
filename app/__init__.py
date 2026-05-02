from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ---------------------------------------------------------------------------
# Cloudinary — configure SDK once at startup using values from app config.
# In production these come from environment variables; in dev they are unset
# and uploads fall back to the local UPLOAD_FOLDER.
# ---------------------------------------------------------------------------
import cloudinary
cloudinary.config(
    cloud_name=app.config.get('CLOUDINARY_CLOUD_NAME'),
    api_key=app.config.get('CLOUDINARY_API_KEY'),
    api_secret=app.config.get('CLOUDINARY_API_SECRET'),
    secure=True,  # always return https:// URLs
)

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# ---------------------------------------------------------------------------
# CORS — read allowed origins from config so the value can be changed per
# environment without touching code.  In production set CORS_ORIGINS to your
# Render domain (e.g. "https://driftdater.onrender.com").
# ---------------------------------------------------------------------------
_cors_origins = [o.strip() for o in app.config.get('CORS_ORIGINS', '*').split(',')]
CORS(app, resources={r"/api/*": {"origins": _cors_origins}}, supports_credentials=True)

# ---------------------------------------------------------------------------
# Absolute path to the Vite build output directory.  Derived from __file__ so
# it works regardless of the directory gunicorn is started from.
# ---------------------------------------------------------------------------
import os
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dist')

# Ensure upload folder exists (used in local development)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from app import views, models
