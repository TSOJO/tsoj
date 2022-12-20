from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Mapping, List, Optional, cast
from pymongo.errors import DuplicateKeyError
import logging

from isolate_wrapper.custom_types import Result, Verdict
from isolate_wrapper import IsolateSandbox

from website.celery_tasks import add_to_db
from website.db import db
from .assignment import Assignment
from .problem import Problem
from .user import User


class Submission:

	_max_id: int = 0

	def __init__(self,
				 username: str,
				 problem: Problem,
				 code: str,
				 final_verdict: Optional[Verdict]=None,
				 results: Optional[List[Result]]=None,
				 id: Optional[int]=None,
				 assignment_id: Optional[int]=None,
				 submission_time: datetime=datetime.utcnow()):
		# Public properties.
		self.username = username
		# Note here we embed `problem` into Submission, because we want to essentially
		# `freeze` the problem instance in time, so any edits made to the problem will
		# will not be reflected on the submission page if checked in the future.
		self.problem = problem
		self.code = code
		if final_verdict is None:
			self.final_verdict = Verdict.WJ
		else:
			self.final_verdict = final_verdict
		if results is None:
			self.results = []
		else:
			self.results = results
		self.id: Optional[int] = id
		self.assignment_id = assignment_id
		self.submission_time = submission_time

	def create_empty_results(self, num_results):
		for _ in range(num_results):
			self.results.append(
				Result(verdict=Verdict.WJ,
           			   time=-1,
                       memory=-1))

	def update_result(self, result_index, verdict, time, memory):
		self.results[result_index] = Result(verdict=verdict,
                                      		time=time,
                                        	memory=memory)
		self.final_verdict = IsolateSandbox.decide_final_verdict(self.results)
		self.save(replace=True)
	
	def tests_completed(self):
		count = 0
		for result in self.results:
			if result.verdict != Verdict.WJ:
				count += 1
		return count

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
			problem=Problem.cast_from_document(document['problem']),
			code=document['code'],
   			final_verdict=Verdict.cast_from_document(document['final_verdict']),
			results=[Result.cast_from_document(result) for result in document['results']],
			assignment_id=document['assignment_id'],
			submission_time=datetime.strptime(document['submission_time'], '%Y-%m-%dT%H:%M:%S.%f')
		)
		return submission_obj

	def cast_to_document(self) -> Dict[str, object]:
		return {
			'_id': self.id,
			'id': self.id,
			'username': self.username,
			'problem': self.problem.cast_to_document(),
			'code': self.code,
			'final_verdict': self.final_verdict.cast_to_document(),
			'results': [result.cast_to_document() for result in self.results],
			'assignment_id': self.assignment_id,
			'submission_time': self.submission_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
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

	def save(self, replace=False, wait=False) -> Submission:
		if not self.id:
			# Generate new incremented ID
			Submission._max_id += 1
			self.id = Submission._max_id
		doc = self.cast_to_document()
		if wait:
			add_to_db('submissions', doc, replace)
		else:
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
