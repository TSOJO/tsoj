from __future__ import annotations
from typing import Any, List, Optional, cast

from bson import ObjectId

from .problem import Problem
from ..db import db

class Assignment:

	"""Properties"""

	problem_ids: List[str]
	_assignment_id: int
	@property
	def assignment_id(self):
		return self._assignment_id
	_object_id: Optional[ObjectId] = None

	async def fetch_problems(self):
		# TODO optimize this with only one query
		return [Problem.find_one({'id': p}) for p in self.problems]

	"""Methods"""
	def __init__(self, problem_ids: List[str]):
		# TODO auto increment id
		self._assignment_id = 1
		self.problem_ids = problem_ids
		pass

	"""Database Wrapper Methods"""

	@classmethod
	def find_one(cls, filter: object) -> Optional[Assignment]:
		result = db.assignments.find_one(filter=filter)
		if result == None: return None
		result = cast(Any, result)
		new = Assignment(**result)
		new._assignment_id = result.assignment_id
		new._object_id = result._id
		return new

	@classmethod
	def find_all(cls, filter: object) -> List[Assignment]:
		results = db.assignments.find(filter=filter)
		news: List[Assignment] = []
		for result in results:
			result = cast(Any, result)
			new = Assignment(**result)
			new._assignment_id = result.assignment_id
			new._object_id = result._id
			news.append(new)
		return news

	async def save(self) -> Assignment:
		if not self._object_id:
			new = db.assignments.insert_one({
				'assignment_id': self._assignment_id,
				'problems': self.problem_ids
			})
			self._object_id = new.inserted_id
		else:
			db.assignments.update_one({
				'_id': self._object_id,
			}, {
				'assignment_id': self._assignment_id,
				'problems': self.problem_ids
			}, upsert=True)

		return self

	# @classmethod
	# def register() -> None:
	# 	if not 'assignments' in db.list_collection_names():
	# 		db.create_collection('assignments')
