from __future__ import annotations

from typing import *

from website.models.db_model import DBModel
from website.models import user as user_module
from website.celery_tasks import add_to_db, delete_from_db
from website.db import db


class UserGroup(DBModel):

    _max_id: int = 0

    def __init__(
        self, name: str, id: int = None, user_ids: Optional[List[int]] = None
    ) -> None:
        self.name = name
        self.id = id
        self._user_ids = [] if user_ids is None else user_ids

    @property
    def user_ids(self) -> List[int]:
        return self._user_ids

    @user_ids.setter
    def user_ids(self, new_user_ids: List[int]) -> None:
        self.save()  # Get ID!
        to_remove = list(set(self.user_ids) - set(new_user_ids))
        to_add = list(set(new_user_ids) - set(self.user_ids))

        for user in user_module.User.find_all({'id': {'$in': to_remove}}):
            user._user_group_ids.remove(self.id)  # very sorry
            user.save(replace=True)

        for user in user_module.User.find_all({'id': {'$in': to_add}}):
            user._user_group_ids.append(self.id)  # forgive me :((((
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
        if not self.id:
            UserGroup._max_id += 1
            self.id = UserGroup._max_id
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
        # Get and store max ID for incrementation.
        all_user_groups = cls.find_all()
        if len(all_user_groups) == 0:
            cls._max_id = 0
        else:
            all_ids = [cast(int, a.id) for a in all_user_groups]
            cls._max_id = max(all_ids)
