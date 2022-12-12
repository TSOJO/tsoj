from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from bson import ObjectId

from isolate_wrapper.custom_types import Result, Verdict

from ..db import db
from .assignment import Assignment
from .problem import Problem
from .user import User


class Submission:

	_max_id: int

	def __init__(self,
				 username: str,
				 final_verdict: Verdict,
				 docs: List[Result],
				 problem_id: str,
				 assignment_id: int,
				 submission_time=datetime.now(), **_):
		# Public properties.
		self.username = username
		self.final_verdict = final_verdict
		self.docs = docs
		self.problem_id = problem_id
		self.assignment_id = assignment_id
		self.submission_time = submission_time

		# Private properties.
		self._id: Optional[int] = None
		self._object_id: Optional[ObjectId] = None

	@property
	def id(self): return self._id

	def fetch_user(self) -> User:
		return cast(User, User.find_one({'username': self.username}))

	def fetch_problem(self) -> Problem:
		return cast(Problem, await Problem.find_one({'id': self.problem_id}))

	def fetch_assignment(self) -> Optional[Assignment]:
		if self.assignment_id is None:
			return None
		return Assignment.find_one({'id': self.assignment_id})

	"""Database Wrapper Methods"""

	@classmethod
	def _cast_from_document(cls, document: Any) -> Submission:
		new = Submission(**document)
		new._id = document['id']
		new._object_id = document['_id']
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'id': self._id,
			'username': self.username,
			'final_verdict': self.final_verdict,
			'docs': self.docs,
			'problem_id': self.problem_id,
			'assignment_id': self.assignment_id,
			'submission_time': self.submission_time,
		}

	@classmethod
	def find_one(cls, filter) -> Submission | None:
		doc = db.submissions.find_one(filter=filter)
		if doc is None:
			return None
		return cls._cast_from_document(doc)

	@classmethod
	def find_all(cls, filter: Dict = {}) -> List[Submission]:
		docs = db.sumbissons.find(filter=filter)
		return [cls._cast_from_document(doc) for doc in docs]

	def save(self) -> Submission:
		# TODO Auto increment submission id
		if not self._object_id:
			doc = self._cast_to_document()

			# Generate new incremented ID
			Submission._max_id += 1
			doc['assignment_id'] = Submission._max_id
			self._id = Submission._max_id

			new = db.submissions.insert_one(doc)
			self._object_id = new.inserted_id
		else:
			db.submissions.replace_one(filter={
				'_id': self._object_id,
			}, replacement=self._cast_to_document(), upsert=True)

		return self

	@classmethod
	def init(cls) -> None:
		# Get and store max ID for incrementation.
		cls._max_id = max([cast(int, s._id) for s in cls.find_all()] or [0])
