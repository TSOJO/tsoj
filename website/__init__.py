from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .problem import problem_bp
from .errors import page_not_found

db = SQLAlchemy()

def init_app() -> Flask:
    # Initial config.
    app: Flask = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    # Initialise database.
    db.init_app(app)
    create_tables(app)
    
    # Register blueprints.
    app.register_blueprint(problem_bp, url_prefix='/problem/')
    
    # Register error handler.    
    app.register_error_handler(404, page_not_found)

    return app

def create_tables(app):
    # Import models.
    from .models import Problem
    with app.app_context():
        # Create tables if they do not exist already.
        db.create_all()
