from __future__ import annotations
from typing import List
from .. import mongo

class Testcase:
  input: str
  # A function that takes in the output and returns a boolean value.
  accepted_outputs: List[str]

class Problem:

  """Properties"""
  id: str
  name: str
  description: str
  time_limit: int
  memory_limit: int
  # A dict with the key being the language, and the value being the list of test cases for that language
  test_cases: List[Testcase]

  """Database Wrapper Methods"""

  @staticmethod
  def find_one(cls, *args) -> Problem:
    # TODO
    pass

  def save(self) -> Problem:
    # TODO
    return self

  @staticmethod
  def register() -> None:
    mongo.prod.create_collection('problems')

  