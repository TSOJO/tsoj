from mongokit import Document
from .. import db

@db.register
class Assignment(Document):
  structure = {
    'id': int,
    'problems': [str]
  }
  required_fields = ['id']
  indexes = {
    'fields': [('id', 1)],
    'unique': True
  }
