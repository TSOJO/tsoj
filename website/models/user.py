from __future__ import annotations

import secrets
from os import environ
from typing import *
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

from website.db import db
from website.celery_tasks import add_to_db, send_email, delete_from_db
from isolate_wrapper.custom_types import Verdict
from website.models.db_model import DBModel
from website.models import submission as submission
from website.models import assignment as assignment


class User(UserMixin, DBModel):
    def __init__(
        self,
        email: str,
        id: str = '',
        username: str = '',
        full_name: str = '',
        plaintext_password: str = '',
        user_group_ids: Optional[List[int]] = None,
        hide_name: bool = False,
        is_admin: bool = False,
    ):
        # Public properties
        self.email = email
        self.id = email.split('@')[0] if id == '' else id
        self.username = self.id if username == '' else username
        self.full_name = full_name
        self.user_group_ids = [] if user_group_ids is None else user_group_ids
        self.is_admin = is_admin
        self.hide_name = hide_name

        # Private properties
        self._hashed_password = generate_password_hash(plaintext_password)

    def get_id(self):
        return self.id

    def set_password(self, plaintext_password):
        self._hashed_password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self._hashed_password, plaintext_password)

    def fetch_submissions(self) -> List[submission.Submission]:
        return submission.Submission.find_all({'user_id': f'{self.id}'}, sort=True)

    def fetch_assignments(self, sort=False) -> List[assignment.Assignment]:
        return assignment.Assignment.find_all(
            {'user_group_ids': {'$in': self.user_group_ids}},
            sort=sort,
        )

    def get_solved_problem_ids(self) -> List[int]:
        problem_ids = set()
        for s in self.fetch_submissions():
            if s.final_verdict == Verdict.AC:
                problem_ids.add(s.problem_id)
        problem_ids = list(problem_ids)
        problem_ids.sort()
        return problem_ids

    def get_attempt(self, problem_id: int) -> Optional[submission.Submission]:
        # Return AC submission if there is one, otherwise return any (if any) attempt.
        ac_submission = submission.Submission.find_one(
            {
                'problem_id': problem_id,
                'final_verdict.verdict': 'AC',
                'user_id': self.id,
            }
        )
        if ac_submission:
            return ac_submission

        # ! Possible bug if find_one doesn't find the most recent one.

        return submission.Submission.find_one(
            {'problem_id': problem_id, 'user_id': self.id}
        )

    def set_password_and_send_email(self):
        password = secrets.token_urlsafe(8)
        self.set_password(password)

        subject = 'Your TSOJ password'
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
            user_group_ids=document['user_group_ids'],
            is_admin=document['is_admin'],
            hide_name=document['hide_name'],
        )
        user_obj._hashed_password = document['hashed_password']
        return user_obj

    def cast_to_document(self) -> Dict[str, Any]:
        return {
            '_id': self.id,
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'hashed_password': self._hashed_password,
            'user_group_ids': self.user_group_ids,
            'is_admin': self.is_admin,
            'hide_name': self.hide_name,
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

    def delete(self, wait=False) -> None:
        if wait:
            delete_from_db('users', self.cast_to_document())
        else:
            delete_from_db.delay('users', self.cast_to_document())
