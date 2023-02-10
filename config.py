from os import environ, path

from dotenv import load_dotenv

base_dir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(base_dir, '.env'))

SECRET_KEY = environ.get('SECRET_KEY')
DEV = environ.get('DEV') == '1'
TONBRIDGE = environ.get('TONBRIDGE') == '1'

DEVELOPERS = environ.get('DEVELOPERS').split()

GMAIL_APP_PWD = environ.get('GMAIL_APP_PWD')
GMAIL_EMAIL = environ.get('GMAIL_EMAIL')

INITIAL_ADMIN_EMAIL = environ.get('INITIAL_ADMIN_EMAIL')
INITIAL_ADMIN_PASSWORD = environ.get('INITIAL_ADMIN_PASSWORD')

if DEV:
    DEBUG = True
    MONGO_URI = 'mongodb://127.0.0.1:27017/tsoj'
    
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
else:
    MONGO_USERNAME = environ.get('MONGO_USERNAME')
    MONGO_PASSWORD = environ.get('MONGO_PASSWORD')
    MONGO_HOSTNAME_PORT = environ.get('MONGO_HOSTNAME_PORT')
    MONGO_DB = environ.get('MONGO_DB')
    MONGO_URI = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOSTNAME_PORT}/{MONGO_DB}?authSource=admin&connectTimeoutMS=2000'
    
    REDIS_PASSWORD = environ.get('REDIS_PASSWORD')
    REDIS_HOSTNAME_PORT = environ.get('REDIS_HOSTNAME_PORT')
    CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOSTNAME_PORT}'
    CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@{REDIS_HOSTNAME_PORT}'