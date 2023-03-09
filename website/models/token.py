import secrets
import hashlib
from typing import Dict, Any, Optional, Mapping, cast
from datetime import datetime, timedelta

from website.celery_tasks import add_to_db, delete_from_db, send_email
from website.db import db
from website.models.db_model import DBModel


class Token(DBModel):
    def __init__(
        self,
        token_data: Dict,
        token_length: int = 16,
        persistent: bool = False,
        action: Optional[str] = None,
        id: Optional[int] = None,
        hashed_token: Optional[str] = None,
        expiration: Optional[datetime] = None,
        ttl: int = 3
    ):
        self.token_data = token_data
        self.token_length = token_length
        self.persistent = persistent
        self._id = id
        
        if action is None:
            self.action = ''
        else:
            self.action = action
        
        if hashed_token is None:
            self.plaintext_token = secrets.token_urlsafe(token_length)
            self.hashed_token = hashlib.md5(self.plaintext_token.encode('utf-8')).hexdigest()
        else:
            self.hashed_token = hashed_token
        
        if expiration is None:
            self.expiration = datetime.utcnow() + timedelta(hours=ttl)
        else:
            self.expiration = expiration
    
    @property
    def id(self):
        if self._id is None:
            try:
                max_id_doc = db.tokens.find(projection={"id": 1, "_id":0}).sort("id", -1)[0]
            except IndexError:
                # collection is empty
                max_id = 0
            else:
                max_id = max_id_doc['id']
            self._id = max_id + 1
        return self._id

    def is_valid(self):
        return self.expiration > datetime.utcnow()
    
    @classmethod
    def get_token_data(cls, plaintext_token, action):
        hashed_token = hashlib.md5(plaintext_token.encode('utf-8')).hexdigest()
        token = Token.find_one(
            {
                'hashed_token': hashed_token,
                'action': action,
            }
        )
        
        if token is None or token.action != action:
            return None
        
        if not token.persistent and not token.is_valid():
            # If token is persistent, we ignore expiration check.
            token.delete()
            return None
        else:
            token_data = token.token_data
            if not token.persistent:
                token.delete()
            return token_data

    @classmethod
    def cast_from_document(cls, document: Any):
        token_obj = Token(
            id=document['id'],
            token_data=document['token_data'],
            token_length=document['token_length'],
            persistent=document['persistent'],
            action=document['action'],
            hashed_token=document['hashed_token'],
            expiration=datetime.strptime(
                document['expiration'], '%Y-%m-%dT%H:%M:%S.%f'
            ),
        )
        return token_obj

    def cast_to_document(self) -> Dict[str, Any]:
        return {
            '_id': self.id,
            'id': self.id,
            'token_data': self.token_data,
            'token_length': self.token_length,
            'persistent': self.persistent,
            'action': self.action,
            'hashed_token': self.hashed_token,
            'expiration': self.expiration.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        }
        
    @classmethod
    def find_one(cls, filter: Mapping[str, Any]):
        result = db.tokens.find_one(filter=filter)
        if result is None:
            return None
        return cls.cast_from_document(result)

    @classmethod
    def find_all(cls, filter: Mapping[str, Any] = None):
        results = db.tokens.find(filter=filter)
        return [cls.cast_from_document(result) for result in results]
    
    def save(self, replace=False, wait=False):
        doc = self.cast_to_document()
        if wait:
            add_to_db('tokens', doc, replace)
        else:
            add_to_db.delay('tokens', doc, replace)
        return self

    def delete(self, wait=False) -> None:
        if wait:
            delete_from_db('tokens', self.cast_to_document())
        else:
            delete_from_db.delay('tokens', self.cast_to_document())
    
    @classmethod
    def init(cls) -> None:
        # Create index for fast max_id query.
        db.tokens.create_index([("id", -1)])
