from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional, cast

from bson import ObjectId

from website.db import db
from . import submission as submission_file
from werkzeug.security import generate_password_hash, check_password_hash

class User:

	def __init__(self, username: str, email: str, plaintext_password: str, **_): 
		# Public properties
		self.username = username
		self.email = email
		
		# Private properties
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

	"""Database Wrapper Methods"""

	@classmethod
	def _cast_from_document(cls, document: Any) -> User:
		new = User(**document)
		new._object_id = document['_id']
		new._hashed_password = document['hashed_password']
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'username': self.username,
			'email': self.email,
			'hashed_password': self._hashed_password,
			'submission_ids': self._submission_ids
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