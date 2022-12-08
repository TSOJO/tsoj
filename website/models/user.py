from __future__ import annotations
from re import match
from typing import List
from .. import mongo
from submission import Submission

class User:
  """Properties"""

  _email: str
  @property
  def email(self) -> str:
    return self._email
  @email.setter
  def email(self, e: str):
    if not match(r'([0-9]{2}[a-zA-Z]+)|([a-zA-Z]+\.[a-zA-Z]+)@tonbridge-school.org', e):
      raise ValueError(f'Email must match /([0-9]{2}[a-zA-Z]+)|([a-zA-Z]+\.[a-zA-Z]+)@tonbridge-school.org/g, recieved "{e}".')
    self._email = e
  
  username: str

  _submissions: List[str]
  @property
  def submissions(self) -> List[Submission]:
    return [Submission.find_one({'id': s}) for s in self._submissions]

  """Methods"""

  def __init__(self, email, username): 
    self.email = email
    self.username = username

  def add_submission(self, newSubmission: Submission, save = True):
    self._submissions.append(newSubmission.id)
    if save:
      self.save()

  """Database Wrapper Methods"""

  @staticmethod
  def find_one(*args) -> User:
    # TODO
    pass

  def save(self) -> User:
    # TODO
    return self

  @staticmethod
  def register() -> None:
    mongo.prod.create_collection('users')

