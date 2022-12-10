from typing import List, Tuple
from celery import Celery

from website.models import Submission, Problem
from isolate_wrapper import IsolateSandbox, Testcase, Result
# from flask_celery import make_celery

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
celery = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery.task(name='judge')
def judge(user_code: str, problem_id: str):
    testcases = [
        Testcase('2\n9\n', '11\n'),
        Testcase('10\n20\n', '30\n'),
    ]
    time_limit = 1
    memory_limit = 1024 * 64
    IsolateSandbox().judge(user_code, testcases, time_limit, memory_limit)
    return 'done'
