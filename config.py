import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'WP3-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
