from __future__ import annotations

from typing import Any, Dict, List, Optional

from isolate_wrapper.custom_types import Testcase
from website.db import db
from website.celery_tasks import add_to_db, delete_from_db
from website.models.db_model import DBModel


class Problem(DBModel):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        time_limit: int,  # ms
        memory_limit: int,  # KB
        testcases: List[Testcase],
        hints: Optional[List] = None,
        num_solves: int = 0,
        is_public: bool = False,
    ):
        # Public properties.
        self.id = id
        self.name = name
        self.description = description
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.testcases = testcases
        self.hints = [] if hints is None else hints
        self.num_solves = num_solves
        self.is_public = is_public

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> Problem:
        return Problem(
            id=document['id'],
            name=document['name'],
            description=document['description'],
            time_limit=document['time_limit'],
            memory_limit=document['memory_limit'],
            testcases=[Testcase(**testcase) for testcase in document['testcases']],
            hints=document['hints'],
            num_solves=document['num_solves'],
            is_public=document['is_public'],
        )

    def cast_to_document(self) -> Dict[str, object]:
        return {
            '_id': self.id,
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'testcases': [testcase.__dict__ for testcase in self.testcases],
            'hints': self.hints,
            'num_solves': self.num_solves,
            'is_public': self.is_public,
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

    def save(self, replace=False, wait=False) -> Problem:
        doc = self.cast_to_document()
        if wait:
            add_to_db('problems', doc, replace=replace)
        else:
            add_to_db.delay('problems', doc, replace=replace)
        return self

    def delete(self, wait=False) -> None:
        if wait:
            delete_from_db('problems', self.cast_to_document())
        else:
            delete_from_db.delay('problems', self.cast_to_document())
