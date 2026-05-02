from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Ensure upload folder exists
import os
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialise Cloudinary SDK when credentials are present (production)
if app.config.get('CLOUDINARY_CLOUD_NAME'):
    import cloudinary
    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET'],
        secure=True,
    )

from app import views, models
