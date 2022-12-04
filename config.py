from os import environ, path
from dotenv import load_dotenv

base_dir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(base_dir, '.env'))

SECRET_KEY = environ.get('SECRET_KEY')
TESTING = True
DEBUG = True

SQLALCHEMY_DATABASE_URI = environ.get('DB_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True  # For debugging.
SQLALCHEMY_ENGINE_OPTIONS = {
    # Supposed to keep connection alive by refreshing connection every 1 hour.
    # (MySQL supposedly closes connection after 8 hours.)
    # ! Not sure if this actually works...
    'pool_recycle': 3600,
}
