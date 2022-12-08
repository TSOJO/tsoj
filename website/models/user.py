from __future__ import annotations
from re import match
from typing import List

from ..db import db
from . import submission as submissionFile

class User:
	"""Properties"""

	_email: str
	@property
	def email(self) -> str:
		return self._email
	@email.setter
	def email(self, e: str):
		if not match(r'([0-9]{2}[a-zA-Z]+)|([a-zA-Z]+\.[a-zA-Z]+)@tonbridge-school.org', e):
			raise ValueError(f'Email must match /([0-9]{2}[a-zA-Z]+)|([a-zA-Z]+\.[a-zA-Z]+)@tonbridge-school.org/g, recieved "{e}".')
		self._email = e
  
	username: str

	_submissions: List[int]
	@property
	def submissions(self) -> List[submissionFile.Submission]:
		return [submissionFile.Submission.find_one({'id': s}) for s in self._submissions]

	"""Methods"""

	def __init__(self, email, username): 
		self.email = email
		self.username = username

	def add_submission(self, newSubmission: submissionFile.Submission, save = True):
		self._submissions.append(newSubmission.id)
		if save:
			self.save()

	"""Database Wrapper Methods"""

	@staticmethod
	def find_one(*args) -> User:
		# TODO
		pass

	def save(self) -> User:
		# TODO
		return self

	@staticmethod
	def register() -> None:
		if not 'users' in db.list_collection_names():
			db.create_collection('users')
