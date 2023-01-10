. ./venv/bin/activate
celery -A website.celery_worker.celery worker --loglevel=INFO