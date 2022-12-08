from __future__ import annotations
from typing import Any, List, Optional, cast

from bson import ObjectId
from ..db import db
from isolate_wrapper import Testcase

class Problem:

	"""Properties"""
	problem_id: str
	name: str
	description: str
	time_limit: int
	memory_limit: int
	test_cases: List[Testcase]
	_object_id: Optional[ObjectId] = None

	"""Methods"""
	def __init__(self, 
		problem_id: str, 
		name: str, 
		description: str, 
		time_limit: int, 
		memory_limit: int, 
		test_cases: List[Testcase]):
		self.problem_id, self.name, self.description, self.time_limit, self.memory_limit, self.test_cases = \
		problem_id, name, description, time_limit, memory_limit, test_cases
		# TODO Validate if problem_id is unique

	"""Database Wrapper Methods"""

	@classmethod
	async def find_one(cls, filter) -> Optional[Problem]:
		result = db.problems.find_one(filter=filter)
		if result == None: return None
		result = cast(Any, result)
		new = Problem(**result)
		new._object_id = result._id
		return new

	@classmethod
	async def find_all(cls, filter) -> List[Problem]:
		# TODO
		pass

	async def save(self) -> Problem:
		# TODO Validate if problem_id is unique
		if not self._object_id:
			new = db.problems.insert_one({
				'problem_id': self.problem_id,
				'name': self.name,
				'description': self.description,
				'time_limit': self.time_limit,
				'memory_limit': self.memory_limit,
				'test_cases': self.test_cases
			})
			self._object_id = new.inserted_id
		else:
			db.problems.update_one({
				'_id': self._object_id,
			}, {
				'problem_id': self.problem_id,
				'name': self.name,
				'description': self.description,
				'time_limit': self.time_limit,
				'memory_limit': self.memory_limit,
				'test_cases': self.test_cases
			}, upsert=True)

		return self

	# @classmethod
	# def register() -> None:
	# 	if not 'problems' in db.list_collection_names():
	# 		db.create_collection('problems')
 