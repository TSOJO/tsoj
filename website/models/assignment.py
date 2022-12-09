from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional, cast

from bson import ObjectId

from website.models.problem import Problem
from website.db import db

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
	def _cast_from_document(cls, document: Any) -> Assignment:
		new = Assignment(**document)
		new._object_id = document._id
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'assignment_id': self.assignment_id,
			'problems': self.problem_ids
		}

	@classmethod
	async def find_one(cls, filter: object) -> Optional[Assignment]:
		result = await asyncio.to_thread(db.assignments.find_one, filter=filter)
		if result == None: return None
		return cls._cast_from_document(result)

	@classmethod
	async def find_all(cls, filter: object) -> List[Assignment]:
		results = await asyncio.to_thread(db.assignments.find, filter=filter)
		return [cls._cast_from_document(result) for result in results]

	async def save(self) -> Assignment:
		if not self._object_id:
			new = await asyncio.to_thread(db.assignments.insert_one, self._cast_to_document())
			self._object_id = new.inserted_id
		else:
			await asyncio.to_thread(db.assignments.update_one,{
				'_id': self._object_id,
			}, self._cast_to_document(), upsert=True)

		return self

	# @classmethod
	# def register() -> None:
	# 	if not 'assignments' in db.list_collection_names():
	# 		db.create_collection('assignments')
