from __future__ import annotations
from typing import List
from flask_pymongo import PyMongo
from flask import current_app

from .problem import Problem
from ..db import db

class Assignment:

		"""Properties"""

		id: int
		problems: List[str]

		"""Methods"""

		def __init__(self, problems: List[str]):
			# TODO auto increment id
			self.id = 1
			self.problems = problems
			pass

		def get_problems(self):
			return [Problem.find_one({'id': p}) for p in self.problems]

		"""Database Wrapper Methods"""

		@staticmethod
		def find_one(*args) -> Assignment:
			# TODO
			pass

		def save(self) -> Assignment:
			# TODO
			return self

		@staticmethod
		def register() -> None:  
			db.create_collection('assignments')
   