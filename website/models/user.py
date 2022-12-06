from mongokit import Document
from .. import db

@db.register
class User(Document):
  structure = {
    'username': str,
    'email': str,
    'submissions': [str]
  },
  required_fields = ['username', 'email']
