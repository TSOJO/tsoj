import asyncio
from typing import *

import website.models as models
from isolate_wrapper import IsolateSandbox
from website import celery
from website.db import db
from pymongo.errors import DuplicateKeyError
import logging

@celery.task(name='judge')
def judge(user_code: str, problem_id: str):
    problem = models.Problem.find_one({'id': problem_id})
    IsolateSandbox().judge(user_code, problem.testcases, problem.time_limit, problem.memory_limit)
    return 'done'

@celery.task(name='insert')
def add_to_db(collection_name : str, document : Dict[str, Any], replace: bool):
    if not replace:
        try:
            db[collection_name].insert_one(document)
        except DuplicateKeyError:
            logging.warning('Attempted to save duplicate document into collection. Use replace=True for replacement.')
            return 'warning: duplicate document'
    else:
        db[collection_name].replace_one({'_id': document._id}, document, upsert=True)  
    return 'done'