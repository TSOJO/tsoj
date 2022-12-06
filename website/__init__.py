from os import environ
from flask import Flask
from mongokit import Connection

# Connect to MongoDB.
db = Connection(host=environ.get('MONGO_CONNECTION_ID'))

def init_app() -> Flask:
    # Initial config.
    app: Flask = Flask(__name__)
    app.config.from_pyfile('../config.py')    
        
    # ! I know you hate this (I do too), but PLEASE don't touch.
    # ! Moving this up results in circular imports.
    
    # Register blueprints.
    from .problem import problem_bp
    app.register_blueprint(problem_bp, url_prefix='/problem/')
    
    # Register error handler.
    from .errors import page_not_found
    app.register_error_handler(404, page_not_found)

    return app
