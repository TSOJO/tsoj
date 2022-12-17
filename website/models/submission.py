from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Mapping, List, Optional, cast
from pymongo.errors import DuplicateKeyError
import logging

from isolate_wrapper.custom_types import Result, Verdict

from website.celery_tasks import add_to_db
from website.db import db
from .assignment import Assignment
from .problem import Problem
from .user import User


class Submission:

	_max_id: int = 0

	def __init__(self,
				 username: str,
				 final_verdict: Verdict,
				 results: List[Result],
				 problem: Problem,
				 id: Optional[int]=None,
				 assignment_id: Optional[int]=None,
				 submission_time=datetime.now()):
		# Public properties.
		self.username = username
		self.final_verdict = final_verdict
		self.results = results
		# Note here we embed `problem` into Submission, because we want to essentially
		# `freeze` the problem instance in time, so any edits made to the problem will
		# will not be reflected on the submission page if checked in the future.
		self.problem = problem
		self.id: Optional[int] = id
		self.assignment_id = assignment_id
		self.submission_time = submission_time

	def fetch_user(self) -> User:
		return cast(User,
					User.find_one({'username': self.username}))

	def fetch_assignment(self) -> Optional[Assignment]:
		if self.assignment_id is None:
			return None
		return cast(Assignment,
					Assignment.find_one({'id': self.assignment_id}))

	"""Database Wrapper Methods"""

	@classmethod
	def cast_from_document(cls, document: Any) -> Submission:
		submission_obj = Submission(
			id=document['id'],
			username=document['username'],
   			final_verdict=Verdict.cast_from_document(document['final_verdict']),
			results=[Result.cast_from_document(result) for result in document['results']],
			problem=Problem.cast_from_document(document['problem']),
			assignment_id=document['assignment_id'],
			submission_time=document['submission_time']
		)
		return submission_obj

	def cast_to_document(self) -> Dict[str, object]:
		return {
			'_id': self.id,
			'id': self.id,
			'username': self.username,
			'final_verdict': self.final_verdict.cast_to_document(),
			'results': [result.cast_to_document() for result in self.results],
			'problem': self.problem.cast_to_document(),
			'assignment_id': self.assignment_id,
			'submission_time': self.submission_time,
		}

	@classmethod
	def find_one(cls, filter: Mapping[str, Any]) -> Optional[Submission]:
		result = db.submissions.find_one(filter=filter)
		if result is None:
			return None
		return cls.cast_from_document(result)

	@classmethod
	def find_all(cls, filter: Mapping[str, Any]=None) -> List[Submission]:
		results = db.submissions.find(filter=filter)
		return [cls.cast_from_document(result) for result in results]

	def save(self, replace=False) -> Submission:
		if not self.id:
			# Generate new incremented ID
			Submission._max_id += 1
			self.id = Submission._max_id
		doc = self.cast_to_document()
		add_to_db.delay('submissions', doc, replace)
		return self

	@classmethod
	def init(cls) -> None:
		# Get and store max ID for incrementation.
		all_submissions = cls.find_all()
		if len(all_submissions) == 0:
			cls._max_id = 0
		else:
			all_ids = [cast(int, a.id) for a in all_submissions]
			cls._max_id = max(all_ids)
