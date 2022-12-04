from os import environ, path
from dotenv import load_dotenv

base_dir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(base_dir, '.env'))

SECRET_KEY = environ.get('SECRET_KEY')
TESTING = True
DEBUG = True

SQLALCHEMY_DATABASE_URI = environ.get('DB_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
