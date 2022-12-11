from website import init_app
# from flask_celery import make_celery

app = init_app()
app.app_context().push()

from website import celery
