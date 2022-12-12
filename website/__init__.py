import asyncio
from os import environ
from flask import Flask
from celery import Celery
from website.models import Assignment, Submission, User, Problem

app: Flask = Flask(__name__)

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
celery = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND, include=['website.celery_tasks'])
class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
celery.Task = ContextTask


def init_app() -> Flask:
    # Initial config.
    app.config.from_pyfile('../config.py')
    
    with app.app_context():
        asyncio.run(Submission.init())
        Assignment.init()
        
    # Register blueprints.
    # ! I know you hate this (I do too), but PLEASE don't touch.
    # ! Moving this up results in circular imports.
    from .problem.routes import problem_bp
    from .admin.routes import admin_bp
    from .assignment.routes import assignment_bp
    from .home.routes import home_bp
    from .api import api_bp
    
    # Register blueprints.
    app.register_blueprint(problem_bp, url_prefix='/problem')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(assignment_bp, url_prefix='/assignment')
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handler.
    from .errors import page_not_found
    app.register_error_handler(404, page_not_found)

    # Testing db, only after reloaded
    # if environ.get('WERKZEUG_RUN_MAIN') == 'true': asyncio.run(test())

    asyncio.run(debug_db())

    return app

async def debug_db():
    from isolate_wrapper import Testcase
    problems_list = [
        {
            'id': 'A1',
            'name': 'Sum',
            'description': 'Given two numbers, print their sum.',
            'time_limit': 1000,
            'memory_limit': 1024 * 64,
            'testcases': [
                Testcase('2\n9\n', '11\n'),
                Testcase('10\n20\n', '30\n'),
            ],
        },
        {
            'id': 'A2',
            'name': 'Difference',
            'description': 'Given two numbers, print their difference.',
            'time_limit': 1000,
            'memory_limit': 1024 * 64,
            'testcases': [
                Testcase('2\n9\n', '-7\n'),
                Testcase('10\n20\n', '-10\n'),
            ],
        }
    ]
    for problem_raw in problems_list:
        problem = Problem(**problem_raw)
        with app.app_context():
            await problem.save()

async def test():
    with app.app_context():
        user = await User.find_one({'username': 'Eden'})
        await user.send_verification_email()
