from __future__ import annotations

from typing import Any, Dict, List, Optional
from pymongo.errors import DuplicateKeyError
import logging

from isolate_wrapper.custom_types import Testcase
from website.db import db
from website.celery_tasks import add_to_db

class Problem:
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 time_limit: int,  # ms
                 memory_limit: int,  # KB
                 testcases: List[Testcase]):
        # Public properties.
        self.id = id
        self.name = name
        self.description = description
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.testcases = testcases

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> Problem:
        return Problem(id=document['id'],
                       name=document['name'],
                       description=document['description'],
                       time_limit=document['time_limit'],
                       memory_limit=document['memory_limit'],
                       testcases=[Testcase(**testcase) for testcase in document['testcases']])

    def cast_to_document(self) -> Dict[str, object]:
        return {
            '_id': self.id,
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'testcases': [testcase.__dict__ for testcase in self.testcases]
        }

    @classmethod
    def find_one(cls, filter={}) -> Optional[Problem]:
        result = db.problems.find_one(filter=filter)
        if result is None:
            return None
        return cls.cast_from_document(result)

    @classmethod
    def find_all(cls, filter={}, sort=True) -> List[Problem]:
        results = db.problems.find(filter=filter)
        problems = [cls.cast_from_document(result) for result in results]
        if sort:
            problems.sort(key=lambda p: p.id)
        return problems

    def save(self, replace=False) -> Problem:
        add_to_db.delay('problems', self.cast_to_document(), replace=replace)
        return self
