from flask import Flask
from .problem import problem_bp
from .errors import page_not_found

def init_app() -> Flask:
    # Initial config.
    app: Flask = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    # Register blueprints.
    app.register_blueprint(problem_bp, url_prefix='/problem/')
    
    # Register error handler.    
    app.register_error_handler(404, page_not_found)

    return app
