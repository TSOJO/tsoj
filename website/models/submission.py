from __future__ import annotations
from datetime import datetime
from typing import List
from .. import mongo
from user import User
from problem import Problem
from assignment import Assignment
from isolate_wrapper import Verdict

class Result:
  verdict: Verdict
  time: float
  memory: float

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
  
  def get_user(self) -> User:
    return User.find_one({'username': self.user})

  def get_problem(self):
    return Problem.find_one({'id': self.problem})

  def get_assignment(self):
    return Assignment.find_one({'id': self.assignment})

  """Database Wrapper Methods"""

  @staticmethod
  def find_one(cls, *args) -> Submission:
    # TODO
    pass

  def save(self) -> Submission:
    # TODO
    return self

  @staticmethod
  def register() -> None:
    mongo.prod.create_collection('submissions')

