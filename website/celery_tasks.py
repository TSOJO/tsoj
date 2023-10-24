from typing import Dict, Optional, Any
import logging
import smtplib
import ssl
from email.message import EmailMessage
from pymongo.errors import DuplicateKeyError

from config import GMAIL_APP_PWD, GMAIL_EMAIL
from isolate_wrapper import IsolateSandbox, SourceCode, Language
import website.models as models
from website import celery
from website.db import db


@celery.task(name='judge', ignore_result=True)
def judge(user_code: str, language_dict, submission_dict, problem_id, grader_source_code_dict):
    submission = models.Submission.cast_from_document(submission_dict)
    problem = models.Problem.find_one({'id': problem_id})
    sandbox = IsolateSandbox()
    testcases = problem.get_testcases()
    submission.create_empty_results(len(testcases))
    source_code = SourceCode(user_code, Language.cast_from_document(language_dict), aqaasm_inputs=problem.aqaasm_inputs, aqaasm_outputs=problem.aqaasm_outputs)
    grader_source_code = SourceCode.cast_from_document(grader_source_code_dict) if grader_source_code_dict is not None else None
    for i, result in enumerate(
        sandbox.judge(
            source_code, testcases, problem.time_limit, problem.memory_limit, grader_source_code
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
