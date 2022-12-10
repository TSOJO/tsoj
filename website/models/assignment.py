from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional, cast

from bson import ObjectId

from website.models.problem import Problem
from website.db import db

class Assignment:

	_max_id: int = 0

	def __init__(self, problem_ids: List[str], **_):
		# Public properties.
		self.problem_ids: List[str] = problem_ids
		
		# Private properties.
		self._id: Optional[int] = None
		self._object_id: Optional[ObjectId] = None

	@property
	def id(self): return self._id

	def add_problem(self, problem_id: str):
		self.problem_ids.append(problem_id)

	async def fetch_problems(self):
		# TODO optimize this with only one query
		return [Problem.find_one({'id': p}) for p in self.problems]

	"""Database Wrapper Methods"""

	@classmethod
	def _cast_from_document(cls, document: Any) -> Assignment:
		new = Assignment(**document)
		new._id = document['id']
		new._object_id = document['_id']
		return new

	def _cast_to_document(self) -> Dict[str, object]:
		return {
			'id': self._id,
			'problem_ids': self.problem_ids
		}

	@classmethod
	async def find_one(cls, filter: object) -> Optional[Assignment]:
		result = await asyncio.to_thread(db.assignments.find_one, filter=filter)
		if result == None: return None
		return cls._cast_from_document(result)

	@classmethod
	async def find_all(cls, filter: object = {}) -> List[Assignment]:
		results = await asyncio.to_thread(db.assignments.find, filter=filter)
		return [cls._cast_from_document(result) for result in results]

	async def save(self) -> Assignment:
		if not self._object_id:
			doc = self._cast_to_document()

			# Generate new incremented ID
			Assignment._max_id += 1
			doc['assignment_id'] = Assignment._max_id
			self._id = Assignment._max_id
			
			new = await asyncio.to_thread(db.assignments.insert_one, doc)
			self._object_id = new.inserted_id
		else:
			await asyncio.to_thread(db.assignments.replace_one,{
				'_id': self._object_id,
			}, self._cast_to_document())

		return self
	@classmethod
	async def init(cls) -> None:
		# Get and store max ID for incrementation.
		cls._max_id = max([cast(int, a._id) for a in await cls.find_all()] or [0])