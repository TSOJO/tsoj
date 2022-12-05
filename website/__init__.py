from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def init_app() -> Flask:
    # Initial config.
    app: Flask = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    # Initialise database.
    db.init_app(app)
    
    # Only run this first time to initialise tables and create hardcoded entries.
    # ! It will give you error because of duplicate key, but doesn't matter
    # ! since the important thing is it is created.
    # create_tables(app)
    
    # ! I know you hate this (I do too), but PLEASE don't touch.
    # ! Moving this up results in circular imports.
    from .problem import problem_bp
    from .problems import problems_bp
    from .errors import page_not_found
    
    # Register blueprints.
    app.register_blueprint(problem_bp, url_prefix='/problem/')
    app.register_blueprint(problems_bp, url_prefix='/problems/')
    
    # Register error handler.
    app.register_error_handler(404, page_not_found)

    return app

def create_tables(app):
    # Import models.
    from .models import Problem
    with app.app_context():
        # Create tables if they do not exist already.
        db.create_all()
        
        # Hardcoded for now.
        problem_info = {
            'id': 'A1',
            'title': 'Sum',
            'description': 'Given two numbers, print their sum.',
        }
        p = Problem(**problem_info)
        db.session.add(p)
        db.session.commit()
