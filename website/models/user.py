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

    def __init__(self,
                 id: str,
                 email: str,
                 username: str = '',
                 full_name: str = '',
                 plaintext_password: str = '',
                 is_admin: bool = False):
        # Public properties
        self.id = id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.is_admin = is_admin
        # ! Probably don't need if just send them their password
        self.is_verified: bool = False

        # Private properties
        self._hashed_password = generate_password_hash(plaintext_password)

    def get_id(self):
        return self.id

    def set_password(self, plaintext_password):
        self._hashed_password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self._hashed_password, plaintext_password)

    def get_submissions(self) -> List[submission_file.Submission]:
        submissions = submission_file.Submission.find_all({'id': f'{self.id}'})
        return submissions

    def get_solved_problem_ids(self) -> List[int]:
        problem_ids = set()
        for s in self.get_submissions():
            if s.final_verdict == Verdict.AC:
                problem_ids.add(s.problem_id)
        problem_ids = list(problem_ids)
        problem_ids.sort()
        return problem_ids

    def set_password_and_send_email(self):
        password = secrets.token_urlsafe(16)
        self.set_password(password)

        subject = 'Verify your email on TSOJ'
        body = (
            f"Hi {self.id},\n\n"
            "Someone has created a TSOJ account using this email. If it is not you, please ignore this email.\n\n"
            f"Your login password is: {password}\n\n"
            "You can change this password in the account settings page. We hope you have a great time in TSOJ.\n\n"
            "Regards,\n"
            "The TSOJ Organization\n"
            "https://github.com/TSOJO/tsoj"
        )

        send_email.delay(subject, body, self.email)

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> User:
        user_obj = User(
            id=document['id'],
            username=document['username'],
            full_name=document['full_name'],
            email=document['email'],
            is_admin=document['is_admin']
        )
        user_obj._hashed_password = document['hashed_password']
        user_obj.is_verified = document['is_verified']
        return user_obj

    def cast_to_document(self) -> Dict[str, Any]:
        return {
            '_id': self.id,
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
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
