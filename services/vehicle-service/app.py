import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
import redis
import click

load_dotenv()
db = SQLAlchemy()
jwt = JWTManager()
migate = Migrate(version_table = 'alembic_version_vehicles')