from flask import Flask

def init_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    from .problem import problem_bp
    
    app.register_blueprint(problem_bp, url_prefix='/problem/')
    
    from .errors import page_not_found
    
    app.register_error_handler(404, page_not_found)

    return app
