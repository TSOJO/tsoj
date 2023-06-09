from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta
from typing import *

from flask import request, url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from isolate_wrapper.custom_types import Verdict
from website.celery_tasks import add_to_db, delete_from_db, send_email
from website.db import db
from website.models import assignment as assignment
from website.models import assignment as assignment_module
from website.models import submission as submission_module
from website.models import user_group as user_group_module
from website.models import token as token_module
from website.models.db_model import DBModel


class User(UserMixin, DBModel):
    def __init__(
        self,
        email: str,
        id: str = None,
        username: str = None,
        full_name: str = None,
        plaintext_password: str = None,
        user_group_ids: Optional[List[int]] = None,
        hide_name: bool = False,
        privilege: int = 0,
    ):
        # Public properties
        self.email = email
        self.id = self.get_id_from_email(email) if id is None else id
        self.username = self.id if username is None else username
        self.full_name = '' if full_name is None else full_name
        self._user_group_ids = [] if user_group_ids is None else user_group_ids
        self.privilege = privilege
        self.hide_name = hide_name

        # Private properties
        plaintext_password = '' if plaintext_password is None else plaintext_password
        self._hashed_password = generate_password_hash(plaintext_password) if plaintext_password else ''

    def __eq__(self, other):
        return self.id == other.id

    def get_id(self):
        return self.id

    @staticmethod
    def get_id_from_email(email):
        return email.split('@')[0]

    @classmethod
    def check_existing(cls, email):
        check_id = cls.get_id_from_email(email)
        if cls.find_one({'$or': [{'id': check_id}, {'email': email}]}):
            return True
        return False

    def set_password(self, plaintext_password):
        self._hashed_password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self._hashed_password, plaintext_password)

    def is_admin(self):
        return self.privilege >= 2
    
    def is_contributor(self):
        return self.privilege >= 1

    def fetch_submissions(self, filter={}) -> List[submission_module.Submission]:
        return submission_module.Submission.find_all(
            {'user_id': f'{self.id}', **filter}, sort=True
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

    def get_assignment_submissions(self, assignment):
        # Return a dictionary of submissions to an assignment made by the user.
        # {problem_id: (all_submissions, overall_verdict)}
        # overall_verdict = 2 when there is an AC somewhere in the submissions.
        # overall_verdict = 1 when submissions are all 'wrong'.
        # overall_verdict = 0 when there are no submissions.
        all_submissions = {}
        for problem_id in assignment.problem_ids:
            problem_submissions = submission_module.Submission.find_all(
                {
                    'problem_id': problem_id,
                    'user_id': self.id,
                }
            )
            problem_submissions.sort(key=lambda x: x.id, reverse=True)
            
            for submission in problem_submissions:
                if submission.final_verdict.is_ac():
                    all_submissions[problem_id] = (problem_submissions, 2)
                    break
            else:  # No AC found
                if problem_submissions:  # Must be wrong
                    all_submissions[problem_id] = (problem_submissions, 1)
                else:  # Nothing!
                    all_submissions[problem_id] = ([], 0)
        return all_submissions
    
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
        token = token_module.Token(token_data={
            'user_id': self.id,
        }, action='change_password')
        plaintext_token = token.save(wait=True).plaintext_token
        
        subject = 'Reset TSOJ password'
        body = (
            f"Hi {self.full_name},\n\n"
            "Someone has requested a password reset of this email. If it was not you, please ignore this email.\n\n"
            "Click this link to reset your password.\n"
            f"{request.url_root[0: -1]}{url_for('user_bp.reset_password', plaintext_token=plaintext_token)}\n\n"
            "This link expires in 3 hours.\n\n"
            "Regards,\n"
            "TSOJ"
        )

        send_email.delay(subject, body, self.email)
    
    def validate_new_email(self, new_email):
        token = token_module.Token(token_data={
            'user_id': self.id,
            'new_email': new_email,
        }, action='change_email')
        plaintext_token = token.save(wait=True).plaintext_token
        
        subject = 'Verify email'
        body = (
            f"Hi {self.full_name},\n\n"
            "Someone has changed their email address to this address. If it was not you, please ignore this email.\n\n"
            "Click this link to verify this address.\n"
            f"{request.url_root[0: -1]}{url_for('user_bp.verify_new_email', plaintext_token=plaintext_token)}\n\n"
            "This link expires in 3 hours.\n\n"
            "Regards,\n"
            "TSOJ"
        )

        send_email.delay(subject, body, new_email)

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
            'privilege': self.privilege,
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

    def save(self, replace=False, wait=False) -> User:
        if wait:
            add_to_db('users', self.cast_to_document(), replace)
        else:
            add_to_db.delay('users', self.cast_to_document(), replace)
        return self

    def delete(self, wait=False) -> None:
        self.user_group_ids = []
        if wait:
            delete_from_db('users', self.cast_to_document())
        else:
            delete_from_db.delay('users', self.cast_to_document())
