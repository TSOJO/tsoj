from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, cast

from bson import ObjectId

from isolate_wrapper.custom_types import Testcase
from website.db import db


class Problem:
	def __init__(self, 
		id: str, 
		name: str, 
		description: str, 
		time_limit: float, 
		memory_limit: float, 
		testcases: List[Testcase], **_):
		# Public properties.
		self.id = id
		self.name = name 
		self.description = description
		self.time_limit = time_limit 
		self.memory_limit = memory_limit
		self.testcases = testcases

		# Private properties
		self._object_id: Optional[ObjectId] = None

	"""Database Wrapper Methods"""

	@classmethod
	def _cast_from_document(cls, document: Any) -> Problem:
		new = Problem(**document)
		new._object_id = document['_id']
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'id': self.id,
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
		if not self._object_id:
			new = await asyncio.to_thread(db.problems.insert_one, self._cast_to_document())
			self._object_id = new.inserted_id
		else:
			await asyncio.to_thread(db.problems.replace_one, {
				'_id': self._object_id,
			}, self._cast_to_document(), upsert=True)

		return self

	# @classmethod
	# def register() -> None:
	# 	if not 'problems' in db.list_collection_names():
	# 		db.create_collection('problems')
 