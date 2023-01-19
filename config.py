from os import environ, path

from dotenv import load_dotenv

base_dir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(base_dir, '.env'))

SECRET_KEY = environ.get('SECRET_KEY')
TESTING = True
DEBUG = True
TONBRIDGE = True

MONGO_URI = environ.get('MONGO_URI')
GMAIL_APP_PWD = environ.get('GMAIL_APP_PWD')
GMAIL_EMAIL = environ.get('GMAIL_EMAIL')
CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = environ.get('CELERY_RESULT_BACKEND')
BASE_URL = environ.get('BASE_URL')