from __future__ import annotations

import secrets
from os import environ
from typing import *
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

from website.db import db
from website.celery_tasks import add_to_db, send_email
from isolate_wrapper.custom_types import Verdict

from . import submission as submission_file


class User(UserMixin):

    def __init__(self, username: str, email: str, plaintext_password: str = '', is_admin: bool = False):
        # Public properties
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.is_verified: bool = False

        # Private properties
        self._hashed_password = generate_password_hash(plaintext_password)

    def get_id(self):
        return self.username

    def set_password(self, plaintext_password):
        self._hashed_password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self._hashed_password, plaintext_password)

    def get_submissions(self) -> List[submission_file.Submission]:
        submissions = submission_file.Submission.find_all({'username': f'{self.username}'})
        return submissions

    def get_solved_problem_ids(self) -> List[int]:
        problem_ids = set()
        for s in self.get_submissions():
            if s.final_verdict == Verdict.AC:
                problem_ids.add(s.problem_id)
        problem_ids = list(problem_ids)
        problem_ids.sort()
        return problem_ids

    def send_verification_email(self):
        # if self._verification_code == '':
        #     self._verification_code = secrets.token_urlsafe(16)
        #     self.save()

        subject = 'Verify your email on TSOJ'
        body = (
		f"Hi {self.username},\n"
        "\n"
		"Verify your email by clicking this link:\n"
		f"{environ.get('BASE_URL')}/auth?code=abc\n"
		)

        send_email.delay(subject, body, self.email)

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> User:
        user_obj = User(
            username=document['username'],
            email=document['email'],
            is_admin=document['is_admin']
        )
        user_obj._hashed_password = document['hashed_password']
        user_obj.is_verified = document['is_verified']
        return user_obj

    def cast_to_document(self) -> Dict[str, Any]:
        return {
            '_id': self.username,
            'username': self.username,
            'email': self.email,
            'hashed_password': self._hashed_password,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin
        }

    @classmethod
    def find_one(cls, filter: Mapping[str, Any]) -> Optional[User]:
        doc = db.users.find_one(filter=filter)
        if doc is None:
            return None
        return cls.cast_from_document(doc)

    @classmethod
    def find_all(cls, filter: Mapping[str, Any] = None) -> List[User]:
        results = db.users.find(filter=filter)
        return [cls.cast_from_document(result) for result in results]

    def save(self, replace=False) -> User:
        add_to_db.delay('users', self.cast_to_document(), replace)
        return self
