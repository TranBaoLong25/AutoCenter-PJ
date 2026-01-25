import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
import redis
import click
from models.listing import Listing
from models.listing_image import ListingImage
from models.watchlist import WatchList
from services.listingService import ListingService
from controllers.controller_api import api_bp

load_dotenv()
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate(version_table = 'alembic_version_listing')

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "secretkey")
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['INTERNAL_SERVICE_TOKEN'] = os.getenv('INTERNAL_SERVICE_TOKEN')
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    app.register_blueprint(api_bp)
    
    return app