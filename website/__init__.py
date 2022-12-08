from os import environ
from flask import Flask
from flask_pymongo import PyMongo
from models.exports import Assignment, User, Problem, Submission

mongo = PyMongo()

def init_app() -> Flask:
    # Initial config.
    app: Flask = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    # Initialise mongo.
    mongo.init_app(app)
    User.register()
    Problem.register()
    Submission.register()
    Assignment.register()
        
    # Register blueprints.
    # ! I know you hate this (I do too), but PLEASE don't touch.
    # ! Moving this up results in circular imports.
    from .problem.routes import problem_bp
    from .problems import problems_bp  # ! needs changing at some point
    from .admin.routes import admin_bp
    
    # Register blueprints.
    app.register_blueprint(problem_bp, url_prefix='/problem')
    app.register_blueprint(problems_bp, url_prefix='/problems')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Register error handler.
    from .errors import page_not_found
    app.register_error_handler(404, page_not_found)

    return app
