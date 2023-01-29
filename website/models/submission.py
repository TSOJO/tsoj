from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Mapping, List, Optional, cast

from isolate_wrapper.custom_types import Result, Verdict
from isolate_wrapper import IsolateSandbox

from website.celery_tasks import add_to_db, delete_from_db
from website.db import db
from website.models.user import User
from website.models.problem import Problem


class Submission:

    _max_id: int = 0

    def __init__(
        self,
        user_id: str,
        problem_id: int,
        code: str,
        final_verdict: Optional[Verdict] = None,
        results: Optional[List[Result]] = None,
        id: Optional[int] = None,
        submission_time: Optional[datetime] = None
    ):
        # Public properties.
        self.user_id = user_id
        self.problem_id = problem_id
        self.code = code
        self.final_verdict = Verdict.WJ if final_verdict is None else final_verdict
        self.results = [] if results is None else results
        self.id: Optional[int] = id
        self.submission_time = datetime.utcnow() if submission_time is None else submission_time

    def create_empty_results(self, num_results):
        self.results = []
        self.final_verdict = Verdict.WJ
        for _ in range(num_results):
            self.results.append(Result.empty())

    def update_result(self, result_index, result: Result):
        self.results[result_index] = result
        self.final_verdict = IsolateSandbox.decide_final_verdict(
            [r.verdict for r in self.results]
        )
        self.save(replace=True, wait=True)
        if self.final_verdict.is_ac():
            previous_submissions = Submission.find_all({'user_id': self.user_id, 'problem_id': self.problem_id, 'final_verdict': self.final_verdict.cast_to_document()})
            if previous_submissions and len(previous_submissions) < 2:
                # User has not solved before
                self.fetch_problem().increment_num_solves()

    def tests_completed(self):
        count = 0
        for result in self.results:
            if result.verdict != Verdict.WJ:
                count += 1
        return count

    def fetch_user(self) -> User:
        return cast(User, User.find_one({'id': self.user_id}))
    
    def fetch_problem(self) -> Problem:
        return cast(Problem, Problem.find_one({'id': self.problem_id}))

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> Submission:
        submission_obj = Submission(
            id=document['id'],
            user_id=document['user_id'],
            problem_id=document['problem_id'],
            code=document['code'],
            final_verdict=Verdict.cast_from_document(document['final_verdict']),
            results=[
                Result.cast_from_document(result) for result in document['results']
            ],
            submission_time=datetime.strptime(
                document['submission_time'], '%Y-%m-%dT%H:%M:%S.%f'
            ),
        )
        return submission_obj

    def cast_to_document(self) -> Dict[str, object]:
        return {
            '_id': self.id,
            'id': self.id,
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'code': self.code,
            'final_verdict': self.final_verdict.cast_to_document(),
            'results': [result.cast_to_document() for result in self.results],
            'submission_time': self.submission_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        }

    @classmethod
    def find_one(cls, filter: Mapping[str, Any]) -> Optional[Submission]:
        result = db.submissions.find_one(filter=filter, sort=[('id', -1)])
        if result is None:
            return None
        return cls.cast_from_document(result)

    @classmethod
    def find_all(cls, filter: Mapping[str, Any] = None, sort=False) -> List[Submission]:
        results = db.submissions.find(filter=filter)
        submissions = [cls.cast_from_document(result) for result in results]
        if sort:
            submissions.sort(key=lambda s: s.id, reverse=True)
        return submissions

    def save(self, replace=False, wait=False) -> Submission:
        if self.id is None:
            # Generate new incremented ID
            Submission._max_id += 1
            self.id = Submission._max_id
        doc = self.cast_to_document()
        if wait:
            add_to_db('submissions', doc, replace)
        else:
            add_to_db.delay('submissions', doc, replace)
        return self

    def delete(self, wait=False) -> None:
        if wait:
            delete_from_db('submissions', self.cast_to_document())
        else:
            delete_from_db.delay('submissions', self.cast_to_document())

    @classmethod
    def init(cls) -> None:
        # Get and store max ID for incrementation.
        all_submissions = cls.find_all()
        if len(all_submissions) == 0:
            cls._max_id = 0
        else:
            all_ids = [cast(int, a.id) for a in all_submissions]
            cls._max_id = max(all_ids)
