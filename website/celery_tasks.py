from typing import Dict, Optional, Any

import website.models as models
from isolate_wrapper import IsolateSandbox
from website import celery
from website.db import db
from pymongo.errors import DuplicateKeyError
import logging

@celery.task(name='judge')
def judge(user_code: str, problem_id: str, username: str, assignment_id: Optional[int]=None):
    problem = models.Problem.find_one({'id': problem_id})
    sandbox = IsolateSandbox()
    final_verdict, results = sandbox.judge(user_code, problem.testcases, problem.time_limit, problem.memory_limit)
    new_submission = models.Submission(username,
                                       final_verdict,
                                       results,
                                       problem,
                                       assignment_id)
    new_submission.save()  # ! Maybe this shouldn't go to celery if we want to request whether `judge` has finished execution.
    return 'done'

@celery.task(name='insert')
def add_to_db(collection_name: str, document: Dict[str, Any], replace: bool):
    if not replace:
        try:
            db[collection_name].insert_one(document)
        except DuplicateKeyError:
            logging.warning('Attempted to save duplicate document into collection. Use replace=True for replacement.')
            return 'warning: duplicate document'
    else:
        db[collection_name].replace_one({'_id': document._id}, document, upsert=True)  
    return 'done'