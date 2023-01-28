import secrets
import hashlib
from typing import Dict, Any, Optional, Mapping, cast
from datetime import datetime, timedelta

from website.celery_tasks import add_to_db, delete_from_db, send_email
from website.db import db
from website.models.db_model import DBModel


class Token(DBModel):
    
    _max_id: int = 0
    
    def __init__(
        self,
        token_data: Dict,
        id: Optional[int] = None,
        action: Optional[str] = None,
        hashed_token: Optional[str] = None,
        expiration: Optional[datetime] = None,
        ttl: int = 3
    ):
        self.token_data = token_data
        self.id = id
        
        if action is None:
            self.action = ''
        else:
            self.action = action
        
        if hashed_token is None:
            self.plaintext_token = secrets.token_urlsafe(16)
            self.hashed_token = hashlib.md5(self.plaintext_token.encode('utf-8')).hexdigest()
            print(self.hashed_token)
        else:
            self.hashed_token = hashed_token
            
        if expiration is None:
            self.expiration = datetime.utcnow() + timedelta(hours=ttl)
        else:
            self.expiration = expiration
    
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
        if not token.is_valid():
            token.delete()
            return None
        else:
            token_data = token.token_data
            token.delete()
            return token_data

    @classmethod
    def cast_from_document(cls, document: Any):
        token_obj = Token(
            id=document['id'],
            token_data=document['token_data'],
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
        if self.id is None:
            # Generate new incremented ID
            Token._max_id += 1
            self.id = Token._max_id
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
        # Get and store max ID for incrementation.
        all_tokens = cls.find_all()
        if len(all_tokens) == 0:
            cls._max_id = 0
        else:
            all_ids = [cast(int, t.id) for t in all_tokens]
            cls._max_id = max(all_ids)
