import asyncio
from os import environ
from flask import Flask
from website.models import Assignment, Submission, User

app: Flask = Flask(__name__)

def init_app() -> Flask:
    # Initial config.
    app.config.from_pyfile('../config.py')
    
    # with app.app_context():
    #     asyncio.run(Submission.init())
    #     asyncio.run(Assignment.init())
        
    # Register blueprints.
    # ! I know you hate this (I do too), but PLEASE don't touch.
    # ! Moving this up results in circular imports.
    from .problem.routes import problem_bp
    from .admin.routes import admin_bp
    from .assignment.routes import assignment_bp
    from .home.routes import home_bp
    
    # Register blueprints.
    app.register_blueprint(problem_bp, url_prefix='/problem')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(assignment_bp, url_prefix='/assignment')
    app.register_blueprint(home_bp, url_prefix='/')
    
    # Register error handler.
    from .errors import page_not_found
    app.register_error_handler(404, page_not_found)

    # Testing db, only after reloaded
    # if environ.get('WERKZEUG_RUN_MAIN') == 'true': asyncio.run(test())

    return app

async def test():
    with app.app_context():
       user = await User.find_one({'username': 'Eden'})
       await user.send_verification_email()
