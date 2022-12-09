from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional, cast

from bson import ObjectId

from website.db import db
from . import submission as submission_file

class User:
	"""Properties"""
  
	username: str
	email: str
	# TODO Implement getter and setter to encrypt password
	password: str
	submission_ids: List[int]

	_object_id: Optional[ObjectId] = None

	
	"""Methods"""

	def __init__(self, username: str, email: str, password: str): 
		self.email = email
		self.username = username
		self.password = password

	async def fetch_submissions(self) -> List[submission_file.Submission]:
		# TODO Optimize this
		return [cast(submission_file.Submission, submission_file.Submission.find_one({'submission_id': s})) for s in self.submission_ids]

	async def add_submission(self, new_submission: submission_file.Submission, save = True):
		self.submission_ids.append(new_submission.submission_id)
		if save:
			await self.save()

	"""Database Wrapper Methods"""

	@classmethod
	def _cast_from_document(cls, document: Any) -> User:
		new = User(**document)
		new._object_id = document._id
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'username': self.username,
			'email': self.email,
			'password': self.password,
			'submission_ids': self.submission_ids
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
			await asyncio.to_thread(db.users.update_one, {
				'_id': self._object_id,
			}, self._cast_to_document(), upsert=True)

		return self

	# @classmethod
	# def register() -> None:
	# 	if not 'users' in db.list_collection_names():
	# 		db.create_collection('users')
