import asyncio

from website.models import Problem
from isolate_wrapper import IsolateSandbox
from website import celery

@celery.task(name='judge')
def judge(user_code: str, problem_id: str):
    loop = asyncio.new_event_loop()
    problem = loop.run_until_complete(Problem.find_one({'id': problem_id}))
    IsolateSandbox().judge(user_code, problem.testcases, problem.time_limit, problem.memory_limit)
    return 'done'
