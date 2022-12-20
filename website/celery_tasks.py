from typing import Dict, Optional, Any

import website.models as models
from isolate_wrapper import IsolateSandbox
from website import celery
from website.db import db
from pymongo.errors import DuplicateKeyError
import logging

@celery.task(name='judge_wrapper')
def get_id_and_judge(user_code: str, problem_id: str, username: str, assignment_id: Optional[int]=None):
    problem = models.Problem.find_one({'id': problem_id})
    new_submission = models.Submission(username=username,
                                       problem=problem,
                                       code=user_code,
                                       assignment_id=assignment_id)
    new_submission.create_empty_results(len(problem.testcases))
    judge.delay(user_code=user_code,
                submission_dict=new_submission.cast_to_document(),
                problem_dict=problem.cast_to_document())
    return new_submission.save(wait=True).id

@celery.task(name='judge')
def judge(user_code: str, submission_dict, problem_dict):  # ! Adding typings for e.g. models.Submission results in circular imports (????)
    submission = models.Submission.cast_from_document(submission_dict)
    problem = models.Problem.cast_from_document(problem_dict)
    sandbox = IsolateSandbox()
    results = []
    for i, result in enumerate(sandbox.judge(user_code, problem.testcases, problem.time_limit, problem.memory_limit)):
        submission.update_result(i, result.verdict, result.time, result.memory)
        results.append(result)
    final_verdict = sandbox.decide_final_verdict([r.verdict for r in results])
    # ! There's a bug where `final_verdict` is WJ even though all testcases are done. Waiting here seems to fix it. Not sure though.
    submission.update_final_verdict(final_verdict, wait=True)
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
        db[collection_name].replace_one({'_id': document['_id']}, document, upsert=True)  
    return 'done'