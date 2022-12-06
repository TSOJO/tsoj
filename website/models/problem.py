from mongokit import Document
from .. import db

@db.register
class Problem(Document):
  use_dot_notation = True
  structure = {
    'id': str,
    'name': str,
    'description': str,
    # In seconds.
    'time_limit': int, 
    # In MBs.
    'memory_limit': int,
    'testcases': [{
      'input': str,
      'output': str
    }]
  }
  required_fields = ['id', 'testcases']
