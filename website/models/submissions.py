from datetime import datetime
from mongokit import Document
from .. import db
from isolate_wrapper.verdict import Verdict
from isolate_wrapper.result import Result

@db.register
class Sumbssion(Document):
  structure = {
    'id': int,
    'username': str,
    'final_verdict': Verdict,
    'results': [Result],
    'problem': [str],
    'submission_id': datetime,
    'assignment_id': [int]
  }
  required_fields = ['id', 'username', 'final_verdict', 'results']
  indexes = {
    'fields': [('id', 1)],
    'unique': True
  }
