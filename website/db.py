# from https://www.mongodb.com/compatibility/setting-up-flask-with-mongodb

from flask import current_app, g
from pymongo.database import Database
from pymongo import MongoClient
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo

def get_db() -> Database:
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:
        db = g._database = PyMongo(current_app).db
        
    return db


# Use LocalProxy to read the global db instance with just `db`
db:Database = LocalProxy(get_db)