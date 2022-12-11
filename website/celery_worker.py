from website import init_app

app = init_app()
app.app_context().push()

from website import celery
