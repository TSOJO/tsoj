from __future__ import annotations
from datetime import datetime
from typing import List

from ..db import db
from .user import User
from .problem import Problem
from .assignment import Assignment
from isolate_wrapper import Verdict, Result

class Submission:

  """Properties"""

  id: int
  user: str
  final_verdict: Verdict
  results: List[Result]
  problem: str
  submission_time: datetime
  assignment: int

  """Methods"""

  def __init__(self, 
    user: str, 
    final_verdict: Verdict, 
    results: List[Result], 
    problem: str, 
    assignment: int, 
    submission_time = datetime.now()):
    self.user = user
    self.final_verdict = final_verdict
    self.results = results
    self.problem = problem
    self.assignment = assignment
    self.submission_time = submission_time
  
  def get_user(self) -> User:
    return User.find_one({'username': self.user})

  def get_problem(self):
    return Problem.find_one({'id': self.problem})

  def get_assignment(self):
    return Assignment.find_one({'id': self.assignment})

  """Database Wrapper Methods"""

  @staticmethod
  def find_one(filter) -> Submission | None:
    # TODO
    query = db.submissions.find_one(filter=filter)
    print(query)
    return None

  def save(self) -> Submission:
    # TODO
    return self

  @staticmethod
  def register() -> None:
    if not 'submissions' in db.list_collection_names():
      db.create_collection('submissions')