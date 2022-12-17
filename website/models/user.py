from __future__ import annotations

import secrets
import smtplib
import ssl
from email.message import EmailMessage
from os import environ
from typing import *

from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

from website.db import db
from website.celery_tasks import add_to_db

from . import submission as submission_file


class User:

    def __init__(self, username: str, email: str, plaintext_password: str=''):
        # Public properties
        self.username = username
        self.email = email

        # Private properties
        self._is_verified: bool = False
        self._verification_code: str = ''
        self._hashed_password = generate_password_hash(plaintext_password)
        self._submission_ids: List[int] = []
        self._object_id: Optional[ObjectId] = None

    def set_password(self, plaintext_password):
        self._hashed_password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self._hashed_password, plaintext_password)

    def fetch_submissions(self) -> List[submission_file.Submission]:
        # TODO Optimize this with one query.
        submissions = []
        for submission_id in self._submission_ids:
            submission = submission_file.Submission.find_one({'id': submission_id})
            submissions.append(cast(submission_file.Submission, submission))
        return submissions

    def add_submission(self, submission_id: int, save=True):
        self._submission_ids.append(submission_id)
        if save:
            self.save()

    def clear_verification_code(self):
        self._verification_code = ''

    def send_verification_email(self):
        print('called')
        if self._verification_code == '':
            self._verification_code = secrets.token_urlsafe(16)
            self.save()

        sender = environ.get('GMAIL_EMAIL')
        pwd = environ.get('GMAIL_APP_PWD')
        print(self.email)
        subject = 'Verify your email on TSOJ'
        body = f'''
		Hi {self.username},

		Verify your email by clicking this link:
		{environ.get('BASE_URL')}/auth?code={self._verification_code}
		'''

        email = EmailMessage()
        email['From'] = sender
        email['To'] = self.email
        email['Subject'] = subject
        email.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls(context=context)
            server.login(sender, pwd)
            print('logged in')
            server.sendmail(sender, self.email, email.as_string())
            print('sent')

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> User:
        user_obj = User(
			username=document['username'],
			email=document['email'],
		)
        user_obj._hashed_password = document['hashed_password']
        user_obj._submission_ids = document['submission_ids']
        user_obj._is_verified = document['is_verified']
        user_obj._verification_code = document['verification_code']
        return user_obj

    def cast_to_document(self) -> Dict[str, Any]:
        return {
            '_id': self.username,
            'username': self.username,
            'email': self.email,
            'hashed_password': self._hashed_password,
            'submission_ids': self._submission_ids,
            'is_verified': self._is_verified,
            'verification_code': self._verification_code
        }

    @classmethod
    def find_one(cls, filter: Mapping[str, Any]) -> Optional[User]:
        doc = db.users.find_one(filter=filter)
        if doc is None:
            return None
        return cls.cast_from_document(doc)

    @classmethod
    def find_all(cls, filter: Mapping[str, Any]=None) -> List[User]:
        results = db.users.find(filter=filter)
        return [cls.cast_from_document(result) for result in results]

    def save(self, replace=False) -> User:
        add_to_db.delay('users', self.cast_to_document(), replace)
        return self
