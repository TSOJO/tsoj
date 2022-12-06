from flask import Flask

def init_app() -> Flask:
    # Initial config.
    app: Flask = Flask(__name__)
    app.config.from_pyfile('../config.py')

    # Register blueprints.
    # ! I know you hate this (I do too), but PLEASE don't touch.
    # ! Moving this up results in circular imports.
    from .problem import problem_bp
    from .problems import problems_bp
    from .assignment import assignment_bp
    app.register_blueprint(problem_bp, url_prefix='/problem/')
    app.register_blueprint(problems_bp, url_prefix='/problems/')
    app.register_blueprint(assignment_bp, url_prefix='/assignment/')
    
    # Register error handler.
    from .errors import page_not_found
    app.register_error_handler(404, page_not_found)

    return app
