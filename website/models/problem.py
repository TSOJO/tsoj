from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, cast

from bson import ObjectId

from isolate_wrapper.custom_types import Testcase
from website.db import db

from pymongo.errors import DuplicateKeyError

class C:
    def __init__(self):
        self._x = None

    def getx(self):
        return self._x

    def setx(self, value):
        self._x = value

    def delx(self):
        del self._x

    x = property(getx, setx, delx, "I'm the 'x' property.")

class Problem:
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 time_limit: float,  # ms
                 memory_limit: float,  # KB
                 testcases: List[Testcase], **_):
        # Public properties.
        self.id = id
        self.name = name
        self.description = description
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.testcases = testcases

    """Database Wrapper Methods"""

    @classmethod
    def _cast_from_document(cls, document: Any) -> Problem:
        return Problem(id=document['id'],
                       name=document['name'],
                       description=document['description'], 
                       time_limit=document['time_limit'] / 1000,
                       memory_limit=document['memory_limit']/1024,
                       testcases=[Testcase(**testcase) for testcase in document['testcases']])

    def _cast_to_document(self) -> Dict[str, object]:
        return {
            '_id': self.id,
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'time_limit': int(round(self.time_limit * 1000)),
            'memory_limit': int(round(self.memory_limit * 1024)),
            'testcases': [testcase.__dict__ for testcase in self.testcases]
        }

    @classmethod
    async def find_one(cls, filter) -> Optional[Problem]:
        result = await asyncio.to_thread(db.problems.find_one, filter=filter)
        if result == None:
            return None
        return cls._cast_from_document(result)

    @classmethod
    async def find_all(cls, filter={}) -> List[Problem]:
        results = await asyncio.to_thread(db.problems.find, filter=filter)
        return [cls._cast_from_document(result) for result in results]

    async def save(self, replace=False) -> Problem:
        if not replace:
            try:
                new = await asyncio.to_thread(db.problems.insert_one, self._cast_to_document())
            except DuplicateKeyError:
                print(
                    'Warning: attempt to insert a document with the same _id. Use replace=True if you want to replace the document.')
        else:
            await asyncio.to_thread(db.problems.replace_one, self._cast_to_document(), upsert=True)
        return self

    # @classmethod
    # def register() -> None:
    # 	if not 'problems' in db.list_collection_names():
    # 		db.create_collection('problems')

