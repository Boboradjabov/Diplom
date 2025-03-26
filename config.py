import os
from pathlib import Path

basedir = Path(__file__).parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-123')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(basedir / 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
