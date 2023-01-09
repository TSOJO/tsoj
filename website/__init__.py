from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from os import environ
from flask import Flask
from celery import Celery
from flask_login import LoginManager
from flask import current_app

celery = Celery(__name__, broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND, include=['website.celery_tasks'])


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    from website.models import User
    return User.find_one({'id': user_id})


def init_app() -> Flask:
    app: Flask = Flask(__name__)
    # Initial config.
    app.config.from_pyfile('../config.py')

    login_manager.init_app(app)
    login_manager.login_view = 'user_bp.login'

    from website.models import Assignment, Submission, User, Problem
    with app.app_context():
        Submission.init()
        Assignment.init()

    # Register blueprints.
    # ! I know you hate this (I do too), but PLEASE don't touch.
    # ! Moving this up results in circular imports.
    from .problem.routes import problem_bp
    from .submission.routes import submission_bp
    from .admin.routes import admin_bp
    from .assignment.routes import assignment_bp
    from .home.routes import home_bp
    from .api import api_bp
    from .user.routes import user_bp

    # Register blueprints.
    app.register_blueprint(problem_bp, url_prefix='/problem')
    app.register_blueprint(submission_bp, url_prefix='/submission')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(assignment_bp, url_prefix='/assignment')
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/user')

    # Register error handler.
    from .errors import page_not_found, unauthorised
    app.register_error_handler(403, unauthorised)
    app.register_error_handler(404, page_not_found)

    debug_db(app)

    @app.route('/send')
    def send():
        test(app)
        return 'sent'

    return app


def debug_db(app):
    from isolate_wrapper import Testcase
    from website.models import Assignment, Submission, User, Problem
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
                Testcase('100\n200\n', '300\n'),
                Testcase('1000\n2000\n', '3000\n'),
                Testcase('10000\n20000\n', '30000\n'),
                Testcase('100000\n200000\n', '300000\n'),
                Testcase('1000000\n2000000\n', '3000000\n'),
                Testcase('10000000\n20000000\n', '30000000\n'),
                Testcase('100000000\n200000000\n', '300000000\n'),
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
            problem.save(replace=True)
    
    assignment = Assignment(creator='JER')
    assignment.add_problems('A1', 'A2')
    with app.app_context():
        assignment.save()

    admin = User(id='admin', email='admin@localhost', plaintext_password='admin', is_admin=True)
    test_user = User(id='user', email='user@localhost', plaintext_password='user', is_admin=False)
    with app.app_context():
        admin.save()
        test_user.save()

def test(app):
    from website.models import Assignment, Submission, User, Problem
    with app.app_context():
        user = User.find_one({'id': 'Justin'})
        user.send_verification_email()
