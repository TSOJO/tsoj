from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional, cast
from isolate_wrapper.custom_types import Testcase

from bson import ObjectId
from website.db import db

class Problem:

	"""Properties"""
	problem_id: str
	name: str
	description: str
	time_limit: int
	memory_limit: int
	testcases: List[Testcase]
	_object_id: Optional[ObjectId] = None

	"""Methods"""
	def __init__(self, 
		problem_id: str, 
		name: str, 
		description: str, 
		time_limit: int, 
		memory_limit: int, 
		testcases: List[Testcase]):
		self.problem_id, self.name, self.description, self.time_limit, self.memory_limit, self.testcases = \
		problem_id, name, description, time_limit, memory_limit, testcases
		# TODO Validate if problem_id is unique

	"""Database Wrapper Methods"""

	@classmethod
	def _cast_from_document(cls, document: Any) -> Problem:
		new = Problem(**document)
		new._object_id = document._id
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'problem_id': self.problem_id,
			'name': self.name,
			'description': self.description,
			'time_limit': self.time_limit,
			'memory_limit': self.memory_limit,
			'testcases': self.testcases
		}

	@classmethod
	async def find_one(cls, filter) -> Optional[Problem]:
		result = await asyncio.to_thread(db.problems.find_one, filter=filter)
		if result == None: return None
		return cls._cast_from_document(result)

	@classmethod
	async def find_all(cls, filter) -> List[Problem]:
		results = await asyncio.to_thread(db.problems.find, filter=filter)
		return [cls._cast_from_document(result) for result in results]

	async def save(self) -> Problem:
		# TODO Validate if problem_id is unique
		if not self._object_id:
			new = await asyncio.to_thread(db.problems.insert_one, self._cast_to_document())
			self._object_id = new.inserted_id
		else:
			await asyncio.to_thread(db.problems.update_one, {
				'_id': self._object_id,
			}, self._cast_to_document(), upsert=True)

		return self

	# @classmethod
	# def register() -> None:
	# 	if not 'problems' in db.list_collection_names():
	# 		db.create_collection('problems')
 