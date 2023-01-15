from __future__ import annotations

from typing import *

from website.models.db_model import DBModel
from website.models.user import User
from website.celery_tasks import add_to_db
from website.db import db


class UserGroup(DBModel):

    _max_id: int = 0

    def __init__(
        self, name: str, id: int = None, user_ids: Optional[List[int]] = None
    ) -> None:
        self.name = name
        self.id = id
        if user_ids is None:
            self.user_ids = []
        else:
            self.user_ids = user_ids

    def fetch_users(self):
        return User.find_all({'id': {'$in': self.user_ids}})

    @classmethod
    def cast_from_document(cls, document: Any) -> UserGroup:
        user_group_obj = UserGroup(
            id=document['id'], name=document['name'], user_ids=document['user_ids']
        )
        return user_group_obj

    def cast_to_document(self) -> Dict[str, object]:
        return {
            '_id': self.id,
            'id': self.id,
            'name': self.name,
            'user_ids': self.user_ids,
        }

    @classmethod
    def find_one(cls, filter: Mapping[str, Any]) -> Optional[UserGroup]:
        result = db.user_groups.find_one(filter=filter)
        if result is None:
            return None
        return cls.cast_from_document(result)

    @classmethod
    def find_all(
        cls, filter: Optional[Mapping[str, Any]] = None, sort=False
    ) -> List[UserGroup]:
        results = db.user_groups.find(filter=filter)
        user_groups = [cls.cast_from_document(result) for result in results]
        if sort:
            user_groups.sort(key=lambda s: s.id, reverse=True)
        return user_groups

    def save(self, replace=False, wait=False) -> UserGroup:
        if not self.id:
            UserGroup._max_id += 1
            self.id = UserGroup._max_id
        doc = self.cast_to_document()
        if wait:
            add_to_db('user_groups', doc, replace)
        else:
            add_to_db.delay('user_groups', doc, replace)
        return self

    @classmethod
    def init(cls) -> None:
        # Get and store max ID for incrementation.
        all_user_groups = cls.find_all()
        if len(all_user_groups) == 0:
            cls._max_id = 0
        else:
            all_ids = [cast(int, a.id) for a in all_user_groups]
            cls._max_id = max(all_ids)
