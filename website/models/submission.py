from __future__ import annotations
from datetime import datetime
from typing import List, Optional, cast
from isolate_wrapper.types import Verdict, Result

from ..db import db
from .user import User
from .problem import Problem
from .assignment import Assignment

class Submission:

	"""Properties"""

	submission_id: int
	user: str
	final_verdict: Verdict
	results: List[Result]
	problem: str
	submission_time: datetime
	assignment: int

	"""Methods"""

	def __init__(self, 
		username: str, 
		final_verdict: Verdict, 
		results: List[Result], 
		problem_id: str, 
		assignment_id: int, 
		submission_time = datetime.now()):
		# TODO Auto increment submission id
		self.submission_id = 1
		self.username = username
		self.final_verdict = final_verdict
		self.results = results
		self.problem_id = problem_id
		self.assignment_id = assignment_id
		self.submission_time = submission_time
  
	async def fetch_user(self) -> User:
		return User.find_one({'username': self.username})

	async def fetch_problem(self) -> Problem:
		return cast(Problem, await Problem.find_one({'id': self.problem_id}))

	async def fetch_assignment(self) -> Optional[Assignment]:
		if self.assignment_id == None: return None
		return Assignment.find_one({'id': self.assignment_id})

	"""Database Wrapper Methods"""

	@classmethod
	def find_one(cls, filter) -> Submission | None:
    	# TODO
		query = db.submissions.find_one(filter=filter)
		print(query)
		return None

	def save(self) -> Submission:
		# TODO
		return self

	# @classmethod
	# def register() -> None:
	# 	if not 'submissions' in db.list_collection_names():
	# 		db.create_collection('submissions')
