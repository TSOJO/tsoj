from typing import Dict, Optional, Any

import website.models as models
from isolate_wrapper import IsolateSandbox
from website import celery
from website.db import db
from pymongo.errors import DuplicateKeyError
import logging
import smtplib
import ssl
from email.message import EmailMessage
from os import environ

@celery.task(name='judge')
def judge(user_code: str, submission_dict, problem_id: int):  # ! Adding typings for e.g. models.Submission results in circular imports (????)
    submission = models.Submission.cast_from_document(submission_dict)
    problem = models.Problem.find_one({'id': problem_id})
    sandbox = IsolateSandbox()
    submission.create_empty_results(len(problem.testcases))
    for i, result in enumerate(sandbox.judge(user_code, problem.testcases, problem.time_limit, problem.memory_limit)):
        submission.update_result(i, result.verdict, result.time, result.memory)
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

@celery.task(name='send_email')
def send_email(subject: str, body: str, to_email : str):
    from_email = environ.get('GMAIL_EMAIL')
    pwd = environ.get('GMAIL_APP_PWD')

    email = EmailMessage()
    email['From'] = from_email
    email['To'] = to_email
    email['Subject'] = subject
    email.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls(context=context)
        server.login(from_email, pwd)
        server.sendmail(from_email, to_email, email.as_string())
    return 'done'