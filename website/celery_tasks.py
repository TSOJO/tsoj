from typing import Dict, Optional, Any
import logging
import smtplib
import ssl
from email.message import EmailMessage
from pymongo.errors import DuplicateKeyError

from config import GMAIL_APP_PWD, GMAIL_EMAIL
from isolate_wrapper import IsolateSandbox, SourceCode
import website.models as models
from website import celery
from website.db import db


@celery.task(name='judge', ignore_result=True)
def judge(user_code: str, language: str, submission_dict, problem_id):
    submission = models.Submission.cast_from_document(submission_dict)
    problem = models.Problem.find_one({'id': problem_id})
    sandbox = IsolateSandbox()
    submission.create_empty_results(len(problem.testcases))
    source_code = SourceCode(user_code, language)
    for i, result in enumerate(
        sandbox.judge(
            source_code, problem.testcases, problem.time_limit, problem.memory_limit
        )
    ):
        submission.update_result(i, result)
    return 'done'


@celery.task(name='insert', ignore_result=True)
def add_to_db(collection_name: str, document: Dict[str, Any], replace: bool):
    if not replace:
        try:
            db[collection_name].insert_one(document)
        except DuplicateKeyError:
            logging.warning(
                'Save failed: attempted to save duplicate document into collection. Use replace=True to replace.'
            )
            return 'save failed: duplicate document'
    else:
        db[collection_name].replace_one({'_id': document['_id']}, document, upsert=True)
    return 'done'


@celery.task(name='delete', ignore_result=True)
def delete_from_db(collection_name: str, document: Dict[str, Any]):
    db[collection_name].delete_one({'_id': document['_id']})
    return 'done'


@celery.task(name='send_email', ignore_result=True)
def send_email(subject: str, body: str, to_email: str):
    from_email = GMAIL_EMAIL
    pwd = GMAIL_APP_PWD

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
