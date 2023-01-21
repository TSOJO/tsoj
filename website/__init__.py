from celery import Celery
from flask import Flask, current_app, request
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['website.celery_tasks'],
)


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
    login_manager.login_message_category = "error"

    from website.models import Assignment, Problem, Submission, User, UserGroup

    with app.app_context():
        Submission.init()
        Assignment.init()
        UserGroup.init()

    # Register blueprints.
    # ! I know you hate this (I do too), but PLEASE don't touch.
    # ! Moving this up results in circular imports.
    from .admin.routes import admin_bp
    from .api import api_bp
    from .assignment.routes import assignment_bp
    from .home.routes import home_bp
    from .problem.routes import problem_bp
    from .submission.routes import submission_bp
    from .user.routes import user_bp

    # Register blueprints.
    app.register_blueprint(problem_bp, url_prefix='/problem')
    app.register_blueprint(submission_bp, url_prefix='/submission')
    app.register_blueprint(assignment_bp, url_prefix='/assignment')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/user')

    # Register error handler.
    from .errors import page_not_found, unauthorised

    app.register_error_handler(403, unauthorised)
    app.register_error_handler(404, page_not_found)

    @app.before_request
    def restrict():
        allowed_endpoints = (
            login_manager.login_view,  # login page
            'user_bp.register',
            'user_bp.static',
            'user_bp.request_password_reset',
            'user_bp.reset_password',
            'static',
        )
        if app.config['DEV']:
            allowed_endpoints += ('user_bp.user_debug', 'user_bp.admin_debug')
        if (not current_user.is_authenticated) and (
            request.endpoint not in allowed_endpoints
        ):
            return login_manager.unauthorized()

    add_initial_admin(app)
    # debug_db(app)
    
    if not app.config['DEV']:
        # This fixes the host header.
        # https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )

    return app


def add_initial_admin(app):
    from website.models import User
    
    admin = User(
        email=app.config['INITIAL_ADMIN_EMAIL'],
        plaintext_password=app.config['INITIAL_ADMIN_PASSWORD'],
        privilege=2,
    )
    
    with app.app_context():
        admin.save(replace=True)


def debug_db(app):
    from isolate_wrapper import Testcase
    from website.models import Assignment, Problem, Submission, User, UserGroup

    problems_list = [
        {
            'id': 'A1',
            'name': 'Sum',
            'description': 'Given two numbers, print their sum.',
            'time_limit': 1000,
            'memory_limit': 1024 * 64,
            'testcases': [
                Testcase('2\n9\n', '11\n', 0),
                Testcase('10\n20\n', '30\n', 0),
                Testcase('100\n200\n', '300\n'),
                Testcase('1000\n2000\n', '3000\n'),
                Testcase('10000\n20000\n', '30000\n'),
                Testcase('100000\n200000\n', '300000\n'),
                Testcase('1000000\n2000000\n', '3000000\n'),
                Testcase('10000000\n20000000\n', '30000000\n'),
                Testcase('100000000\n200000000\n', '300000000\n'),
            ],
            'is_public': True,
        },
        {
            'id': 'A2',
            'name': 'Difference',
            'description': 'Given two numbers, print their difference.',
            'time_limit': 1000,
            'memory_limit': 1024 * 64,
            'testcases': [
                Testcase('2\n9\n', '-7\n', 0),
                Testcase('10\n20\n', '-10\n', 0),
            ],
            'is_public': True,
        },
    ]
    for problem_raw in problems_list:
        problem = Problem(**problem_raw)
        with app.app_context():
            problem.save(replace=True)

    user_group = UserGroup(id=1, name='4A1', user_ids=['admin', 'user'])
    with app.app_context():
        user_group.save(replace=True)

    assignment = Assignment(id=1, creator='JER', user_group_ids=[1])
    assignment.add_problems('A1', 'A2')
    with app.app_context():
        assignment.save(replace=True)

    admin = User(
        id='admin',
        username='admin_name',
        full_name='admin_full_name',
        email='admin@localhost',
        plaintext_password='admin',
        user_group_ids=[1],
        privilege=2,
        hide_name=True,
    )
    test_user = User(
        id='user',
        username='user_name',
        full_name='user_full_name',
        email='user@localhost',
        plaintext_password='user',
        user_group_ids=[1],
        privilege=1,
    )
    with app.app_context():
        admin.save(replace=True)
        test_user.save(replace=True)
