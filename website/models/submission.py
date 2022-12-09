from __future__ import annotations
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from bson import ObjectId
from isolate_wrapper.custom_types import Verdict, Result

from ..db import db
from .user import User
from .problem import Problem
from .assignment import Assignment

class Submission:

	"""Properties"""

	# Unknown until saved
	submission_id: int
	user: str
	final_verdict: Verdict
	docs: List[Result]
	problem_id: str
	submission_time: datetime
	assignment: int

	_object_id: Optional[ObjectId] = None

	"""Methods"""

	def __init__(self, 
		username: str, 
		final_verdict: Verdict, 
		docs: List[Result], 
		problem_id: str, 
		assignment_id: int, 
		submission_time = datetime.now()):
		self.username, self.final_verdict, self.docs, self.problem_id, self.assignment_id, self.submission_time = \
		username, final_verdict,docs,problem_id,assignment_id,submission_time
  
	async def fetch_user(self) -> User:
		return cast(User, await User.find_one({'username': self.username}))

	async def fetch_problem(self) -> Problem:
		return cast(Problem, await Problem.find_one({'id': self.problem_id}))

	async def fetch_assignment(self) -> Optional[Assignment]:
		if self.assignment_id == None: return None
		return await Assignment.find_one({'id': self.assignment_id})

	"""Database Wrapper Methods"""

	@classmethod
	def _cast_from_document(cls, document: Any) -> Submission:
		new = Submission(**document)
		new.assignment_id = document.assignment_id
		new._object_id = document._id
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'username': self.username,
			'final_verdict': self.final_verdict,
			'docs': self.docs,
			'problem_id': self.problem_id,
			'assignment_id': self.assignment_id,
			'submission_time': self.submission_time,
			'assignment': self.assignment
		}

	@classmethod
	async def find_one(cls, filter) -> Submission | None:
		doc = await asyncio.to_thread(db.submissions.find_one, filter=filter)
		if doc == None: return None
		return cls._cast_from_document(doc)

	@classmethod
	async def find_all(cls, filter) -> List[Submission]:
		docs = await asyncio.to_thread(db.sumbissons.find, filter=filter)
		return [cls._cast_from_document(doc) for doc in docs]

	async def save(self) -> Submission:
		# TODO Auto increment submission id
		if not self._object_id:
			new = await asyncio.to_thread(db.submissions.insert_one, self._cast_to_document())
			self._object_id = new.inserted_id
		else:
			await asyncio.to_thread(db.submissions.update_one, {
				'_id': self._object_id,
			}, self._cast_to_document(), upsert=True)

		return self

	# @classmethod
	# def register() -> None:
	# 	if not 'submissions' in db.list_collection_names():
	# 		db.create_collection('submissions')
