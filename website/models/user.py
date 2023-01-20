from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta
from typing import *

from flask import request, url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from config import BASE_URL
from isolate_wrapper.custom_types import Verdict
from website.celery_tasks import add_to_db, delete_from_db, send_email
from website.db import db
from website.models import assignment as assignment
from website.models import assignment as assignment_module
from website.models import submission as submission_module
from website.models import user_group as user_group_module
from website.models.db_model import DBModel


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
        privilege: int = 0,
        password_reset_token_expiration: Optional[datetime] = None
    ):
        # Public properties
        self.email = email
        self.id = email.split('@')[0] if id == '' else id
        self.username = self.id if username == '' else username
        self.full_name = full_name
        self._user_group_ids = [] if user_group_ids is None else user_group_ids
        self.privilege = privilege
        self.hide_name = hide_name
        self.password_reset_token_expiration: Optional[datetime] = password_reset_token_expiration

        # Private properties
        self._hashed_password = generate_password_hash(plaintext_password)
        self._hashed_token = None

    def __eq__(self, other):
        return self.id == other.id

    def get_id(self):
        return self.id

    def set_password(self, plaintext_password):
        self._hashed_password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self._hashed_password, plaintext_password)

    def set_password_reset_token(self, plaintext_token):
        self._hashed_token = generate_password_hash(plaintext_token)
    
    def check_password_reset_token(self, plaintext_token):
        # TODO: Make this a classmethod and find (preferably all at once).
        return self._hashed_token and check_password_hash(self._hashed_token, plaintext_token) and self.password_reset_token_expiration > datetime.utcnow()

    def clear_password_reset_token(self):
        self._hashed_token = None

    def is_admin(self):
        return self.privilege >= 2
    
    def is_contributor(self):
        return self.privilege >= 1

    def fetch_submissions(self) -> List[submission_module.Submission]:
        return submission_module.Submission.find_all(
            {'user_id': f'{self.id}'}, sort=True
        )

    def fetch_assignments(self, sort=False) -> List[assignment_module.Assignment]:
        return assignment_module.Assignment.find_all(
            {'user_group_ids': {'$in': self.user_group_ids}},
            sort=sort,
        )

    def fetch_user_groups(self):
        return user_group_module.UserGroup.find_all(
            {'id': {'$in': self.user_group_ids}}
        )

    def get_solved_problem_ids(self) -> List[int]:
        problem_ids = set()
        for s in self.fetch_submissions():
            if s.final_verdict == Verdict.AC:
                problem_ids.add(s.problem_id)
        problem_ids = list(problem_ids)
        problem_ids.sort()
        return problem_ids

    def get_attempt(self, problem_id: int) -> Optional[submission_module.Submission]:
        # Return latest AC submission if there is one, otherwise return the latest (if any) attempt.
        ac_submission = submission_module.Submission.find_one(
            {
                'problem_id': problem_id,
                'final_verdict.verdict': 'AC',
                'user_id': self.id,
            }
        )
        if ac_submission:
            return ac_submission
        return submission_module.Submission.find_one(
            {'problem_id': problem_id, 'user_id': self.id}
        )

    @property
    def user_group_ids(self) -> List[int]:
        return self._user_group_ids

    @user_group_ids.setter
    def user_group_ids(self, new_user_group_ids: List[int]):
        to_remove = list(set(self.user_group_ids) - set(new_user_group_ids))
        to_add = list(set(new_user_group_ids) - set(self.user_group_ids))
        for user_group in user_group_module.UserGroup.find_all({'id': {'$in': to_remove}}):
            if self.id in user_group.user_ids:
                user_group.user_ids.remove(self.id) 
                user_group.save(replace=True)
        for user_group in user_group_module.UserGroup.find_all({'id': {'$in': to_add}}):
            user_group.user_ids.append(self.id)
            user_group.save(replace=True)
        self._user_group_ids = new_user_group_ids

    def add_to_user_group(self, user_group_id: int):
        user_group_obj = user_group_module.UserGroup.find_one({'id': user_group_id})
        if user_group_obj is None:
            logging.error(f'UserGroup {user_group_id} does not exist.')
            return
        if user_group_id not in self.user_group_ids:
            self.user_group_ids.append(user_group_id)
            self.save(replace=True)
        if self.id not in user_group_obj.user_ids:
            user_group_obj.user_ids.append(id)
            user_group_obj.save(replace=True)

    def set_password_and_send_email(self):
        password = secrets.token_urlsafe(8)

        subject = 'Your TSOJ password'
        body = (
            f"Hi {self.full_name},\n\n"
            "Someone has created a TSOJ account using this email. If it was not you, please ignore this email.\n\n"
            f"Your login password is: {password}\n\n"
            "You can change your password in the account settings page. We hope you have a great time in TSOJ.\n\n"
            "Regards,\n"
            "TSOJ"
        )

        send_email.delay(subject, body, self.email)
        
        self.set_password(password)

    def send_reset_password_email(self):
        token = secrets.token_urlsafe(10)
        subject = 'Reset TSOJ password'
        body = (
            f"Hi {self.full_name},\n\n"
            "Someone has created a requested a password reset of this email. If it was not you, please ignore this email.\n\n"
            "Click this link to reset your password.\n"
            f"{request.url_root[0: -1]}{url_for('user_bp.reset_password', token=token)}\n"
            "This link expires in 3 hours.\n"
            "Regards,\n"
            "TSOJ"
        )

        send_email.delay(subject, body, self.email)

        self.set_password_reset_token(token)
        self.password_reset_token_expiration = datetime.utcnow() + timedelta(hours = 3)

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> User:
        user_obj = User(
            id=document['id'],
            username=document['username'],
            full_name=document['full_name'],
            email=document['email'],
            user_group_ids=document['user_group_ids'],
            privilege=document['privilege'],
            hide_name=document['hide_name'],
            password_reset_token_expiration=datetime.strptime(
                document['password_reset_token_expiration'], '%Y-%m-%dT%H:%M:%S.%f'
            ) if document['password_reset_token_expiration'] else None
        )
        user_obj._hashed_token = document['hashed_token']
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
            'hashed_token': self._hashed_token,
            'user_group_ids': self.user_group_ids,
            'privilege': self.privilege,
            'hide_name': self.hide_name,
            'password_reset_token_expiration': self.password_reset_token_expiration
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

    def save(self, replace=False, wait=False) -> User:
        if wait:
            add_to_db('users', self.cast_to_document(), replace)
        else:
            add_to_db.delay('users', self.cast_to_document(), replace)
        return self

    def delete(self, wait=False) -> None:
        if wait:
            delete_from_db('users', self.cast_to_document())
        else:
            delete_from_db.delay('users', self.cast_to_document())
