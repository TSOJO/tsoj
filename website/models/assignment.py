from __future__ import annotations

from typing import Any, Mapping, Dict, List, Optional, cast
from datetime import datetime

from website.db import db
from website.models.problem import Problem
from website.celery_tasks import add_to_db, delete_from_db
from website.models.db_model import DBModel


class Assignment(DBModel):
    def __init__(
        self,
        creator: str,
        id: Optional[int] = None,
        problem_ids: List[str] = None,
        user_group_ids: List[int] = None,
        visible: bool = False,
        set_time: datetime = None,
    ):
        # Public properties.
        self._id: Optional[int] = id
        self.problem_ids = [] if problem_ids is None else problem_ids
        self.user_group_ids = [] if user_group_ids is None else user_group_ids
        self.creator = creator
        self.visible = visible
        self.set_time = datetime.utcnow() if set_time is None else set_time

    @property
    def id(self):
        if self._id is None:
            try:
                max_id_doc = db.assignments.find(projection={"id": 1, "_id":0}).sort("id", -1)[0]
            except IndexError:
                # collection is empty
                max_id = 0
            else:
                max_id = max_id_doc['id']
            self._id = max_id + 1
        return self._id

    def add_problems(self, *problem_ids):
        self.problem_ids.extend(problem_ids)

    def fetch_problems(self):
        return Problem.find_all({'id': {'$in': self.problem_ids}})

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> Assignment:
        assignment_obj = Assignment(
            id=document['id'],
            problem_ids=document['problem_ids'],
            creator=document['creator'],
            user_group_ids=document['user_group_ids'],
            visible=document['visible'],
            set_time=datetime.strptime(
                document['set_time'], '%Y-%m-%dT%H:%M:%S.%f'),
        )
        return assignment_obj

    def cast_to_document(self) -> Dict[str, object]:
        return {
            '_id': self.id,
            'id': self.id,
            'problem_ids': self.problem_ids,
            'creator': self.creator,
            'user_group_ids': self.user_group_ids,
            'visible': self.visible,
            'set_time': self.set_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        }

    @classmethod
    def find_one(cls, filter: Mapping[str, Any]) -> Optional[Assignment]:
        result = db.assignments.find_one(filter=filter)
        if result is None:
            return None
        return cls.cast_from_document(result)

    @classmethod
    def find_all(
        cls, filter: Optional[Mapping[str, Any]] = None, sort=False, **kwargs
    ) -> List[Assignment]:
        if sort:
            kwargs['sort'] = [('id', -1)]
        results = db.assignments.find(filter=filter, **kwargs)
        assignments = [cls.cast_from_document(result) for result in results]
        return assignments

    def save(self, replace=False, wait=False) -> Assignment:
        doc = self.cast_to_document()
        if wait:
            add_to_db('assignments', doc, replace)
        else:
            add_to_db.delay('assignments', doc, replace)
        return self

    def delete(self, wait=False) -> None:
        if wait:
            delete_from_db('assignments', self.cast_to_document())
        else:
            delete_from_db.delay('assignments', self.cast_to_document())

    @classmethod
    def init(cls) -> None:
        # Create index for fast max_id query.
        db.assignments.create_index([("id", -1)])
