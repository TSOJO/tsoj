from __future__ import annotations

from typing import Any, Mapping, Dict, List, Optional, cast

from website.db import db
from website.models.problem import Problem
from website.celery_tasks import add_to_db


class Assignment:

    _max_id: int = 0

    def __init__(self, id: Optional[int]=None, problem_ids: Optional[List[str]]=None):
        if problem_ids is None:
            problem_ids = []
        # Public properties.
        self.problem_ids: List[str] = problem_ids
        self.id: Optional[int] = id

        # Private properties.
        # self._id: Optional[int] = None

    def add_problems(self, *problem_ids):
        self.problem_ids.extend(problem_ids)

    def fetch_problems(self):
        # TODO optimize this with only one query
        return [Problem.find_one({'id': p}) for p in self.problem_ids]

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> Assignment:
        assignment_obj = Assignment(
            id=document['id'],
            problem_ids=document['problem_ids'],
        )
        return assignment_obj

    def cast_to_document(self) -> Dict[str, object]:
        return {
            '_id': self.id,
            'id': self.id,
            'problem_ids': self.problem_ids
        }

    @classmethod
    def find_one(cls, filter: Mapping[str, Any]) -> Optional[Assignment]:
        result = db.assignments.find_one(filter=filter)
        if result is None:
            return None
        return cls.cast_from_document(result)

    @classmethod
    def find_all(cls, filter: Optional[Mapping[str, Any]]=None, sort=False) -> List[Assignment]:
        results = db.assignments.find(filter=filter)
        assignments = [cls.cast_from_document(result) for result in results]
        if sort:
            assignments.sort(key=lambda s:s.id, reverse=True)
        return assignments

    def save(self, replace=False, wait=False) -> Assignment:
        if not self.id:
            Assignment._max_id += 1
            self.id = Assignment._max_id
        doc = self.cast_to_document()
        if wait:
            add_to_db('assignments', doc, replace)
        else:
            add_to_db.delay('assignments', doc, replace)
        return self

    @classmethod
    def init(cls) -> None:
        # Get and store max ID for incrementation.
        all_assignments = cls.find_all()
        if len(all_assignments) == 0:
            cls._max_id = 0
        else:
            all_ids = [cast(int, a.id) for a in all_assignments]
            cls._max_id = max(all_ids)
