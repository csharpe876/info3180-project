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

from app import views, models
