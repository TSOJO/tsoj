from __future__ import annotations

import asyncio
import secrets
import smtplib
import ssl
from email.message import EmailMessage
from os import environ
from typing import Any, Dict, List, Optional, cast
from uuid import uuid4

from bson import ObjectId
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash

from website.db import db

from . import submission as submission_file


class User:

	def __init__(self, username: str, email: str, plaintext_password: str = '', **_): 
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

	async def fetch_submissions(self) -> List[submission_file.Submission]:
		# TODO Optimize this with one query.
		return [cast(submission_file.Submission, await asyncio.to_thread(submission_file.Submission.find_one, {'submission_id': s})) for s in self._submission_ids]

	async def add_submission(self, submission_id: int, save = True):
		self._submission_ids.append(submission_id)
		if save:
			await self.save()

	def clear_verification_code(self):
		self._verification_code = ''

	async def send_verification_email(self):
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
			await asyncio.to_thread(server.starttls, context=context)
			await asyncio.to_thread(server.login, sender, pwd)
			print('logged in')
			await asyncio.to_thread(server.sendmail, sender, self.email, email.as_string())
			print('sent')

	"""Database Wrapper Methods"""

	@classmethod
	def _cast_from_document(cls, document: Any) -> User:
		new = User(**document)
		new._object_id = document['_id']
		new._hashed_password = document['hashed_password']
		new._is_verified = document['is_verified']
		new._verification_code = document['verification_code']
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'username': self.username,
			'email': self.email,
			'hashed_password': self._hashed_password,
			'submission_ids': self._submission_ids,
			'is_verified': self._is_verified,
			'verification_code': self._verification_code
		}

	@classmethod
	async def find_one(cls, filter) -> Optional[User]:
		doc = await asyncio.to_thread(db.users.find_one, filter)
		if doc == None: return None
		return cls._cast_from_document(doc)
	
	@classmethod
	async def find_all(cls, filter) -> List[User]:
		docs = await asyncio.to_thread(db.users.find, filter)
		return [cls._cast_from_document(doc) for doc in docs]

	async def save(self) -> User:
		if not self._object_id:
			new = await asyncio.to_thread(db.users.insert_one, self._cast_to_document())
			self._object_id = new.inserted_id
		else:
			await asyncio.to_thread(db.users.replace_one, {
				'_id': self._object_id,
			}, self._cast_to_document(), upsert=True)

		return self