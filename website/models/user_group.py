from __future__ import annotations

from typing import *

from website.models.db_model import DBModel
from website.models import user as user_module
from website.celery_tasks import add_to_db, delete_from_db
from website.db import db


class UserGroup(DBModel):
    def __init__(
        self, name: str, id: int = None, user_ids: Optional[List[int]] = None
    ) -> None:
        self.name = name
        self._id = id
        self._user_ids = [] if user_ids is None else user_ids

    @property
    def id(self):
        if self._id is None:
            try:
                max_id_doc = db.user_groups.find(projection={"id": 1, "_id":0}).sort("id", -1)[0]
            except IndexError:
                # collection is empty
                max_id = 0
            else:
                max_id = max_id_doc['id']
            self._id = max_id + 1
        return self._id

    @property
    def user_ids(self) -> List[int]:
        return self._user_ids

    @user_ids.setter
    def user_ids(self, new_user_ids: List[int]) -> None:
        if self.id is None:
            self.save(wait=True)
        to_remove = list(set(self.user_ids) - set(new_user_ids))
        to_add = list(set(new_user_ids) - set(self.user_ids))
        for user in user_module.User.find_all({'id': {'$in': to_remove}}):
            if self.id in user.user_group_ids:
                user.user_group_ids.remove(self.id)
                user.save(replace=True)
        for user in user_module.User.find_all({'id': {'$in': to_add}}):
            user.user_group_ids.append(self.id)
            user.save(replace=True)
        self._user_ids = new_user_ids

    def fetch_users(self):
        return user_module.User.find_all({'id': {'$in': self.user_ids}})

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
        doc = self.cast_to_document()
        if wait:
            add_to_db('user_groups', doc, replace)
        else:
            add_to_db.delay('user_groups', doc, replace)
        return self

    def delete(self, wait=False) -> None:
        self.user_ids = []
        if wait:
            delete_from_db('user_groups', self.cast_to_document())
        else:
            delete_from_db.delay('user_groups', self.cast_to_document())

    @classmethod
    def init(cls) -> None:
        # Create index for fast max_id query.
        db.user_groups.create_index([("id", -1)])
