from __future__ import annotations

from typing import Any, Dict, List, Optional

from isolate_wrapper import Testcase, Language, SourceCode, Verdict
from website.db import db
from website.celery_tasks import add_to_db, delete_from_db
from website.models.db_model import DBModel


class Problem(DBModel):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        time_limit: int,  # ms
        memory_limit: int,  # KB
        testcases: List[Testcase],
        hints: Optional[List[str]] = None,
        allowed_languages: Optional[List[Language]] = None,
        grader_source_code: Optional[SourceCode] = None,
        num_solves: int = 0,
        is_public: bool = False,
        aqaasm_inputs: Optional[List[str]] = None,
        aqaasm_outputs: Optional[List[str]] = None,
        generate_input_code: Optional[SourceCode] = None,
        generate_answer_code: Optional[SourceCode] = None,
    ):
        # Public properties.
        self.id = id
        self.name = name
        self.description = description
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.testcases = testcases
        self.hints = [] if hints is None else hints
        self.allowed_languages = allowed_languages
        self.grader_source_code = grader_source_code
        self.num_solves = num_solves
        self.is_public = is_public
        self.aqaasm_inputs = [] if aqaasm_inputs is None else aqaasm_inputs
        self.aqaasm_outputs = [] if aqaasm_outputs is None else aqaasm_outputs
        self.generate_input_code = generate_input_code
        self.generate_answer_code = generate_answer_code

    def increment_num_solves(self):
        # ! Possibly not needed
        self.num_solves += 1
        self.save(replace=True)
    
    def update_num_solves(self):
        self.num_solves = len(db.submissions.distinct(
            'user_id',
            {
                'problem_id': self.id,
                'final_verdict': Verdict.AC.cast_to_document()
            }
        ))
        self.save(replace=True)

    """Database Wrapper Methods"""

    @classmethod
    def cast_from_document(cls, document: Any) -> Problem:
        return Problem(
            id=document['id'],
            name=document['name'],
            description=document['description'],
            time_limit=document['time_limit'],
            memory_limit=document['memory_limit'],
            testcases=[Testcase.cast_from_document(testcase) for testcase in document['testcases']],
            hints=document['hints'],
            allowed_languages=[Language.cast_from_document(language) for language in document['allowed_languages']] if document['allowed_languages'] is not None else None,
            grader_source_code=SourceCode.cast_from_document(document['grader_source_code']) if document['grader_source_code'] is not None else None,
            num_solves=document['num_solves'],
            is_public=document['is_public'],
            aqaasm_inputs=document['aqaasm_inputs'],
            aqaasm_outputs=document['aqaasm_outputs'],
            generate_input_code=SourceCode.cast_from_document(document['generate_input_code']) if document['generate_input_code'] is not None else None,
            generate_answer_code=SourceCode.cast_from_document(document['generate_answer_code']) if document['generate_answer_code'] is not None else None,
        )

    def cast_to_document(self) -> Dict[str, object]:
        return {
            '_id': self.id,
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'testcases': [testcase.cast_to_document() for testcase in self.testcases],
            'hints': self.hints,
            'allowed_languages': [language.cast_to_document() for language in self.allowed_languages] if self.allowed_languages is not None else None,
            'grader_source_code': self.grader_source_code.cast_to_document() if self.grader_source_code is not None else None,
            'num_solves': self.num_solves,
            'is_public': self.is_public,
            'aqaasm_inputs': self.aqaasm_inputs,
            'aqaasm_outputs': self.aqaasm_outputs,
            'generate_input_code': self.generate_input_code.cast_to_document() if self.generate_input_code is not None else None,
            'generate_answer_code': self.generate_answer_code.cast_to_document() if self.generate_answer_code is not None else None,
        }

    @classmethod
    def find_one(cls, filter={}) -> Optional[Problem]:
        result = db.problems.find_one(filter=filter)
        if result is None:
            return None
        return cls.cast_from_document(result)

    @classmethod
    def find_all(cls, filter={}, sort=True) -> List[Problem]:
        results = db.problems.find(filter=filter)
        problems = [cls.cast_from_document(result) for result in results]
        if sort:
            problems.sort(key=lambda p: p.id)
        return problems

    def save(self, replace=False, wait=False) -> Problem:
        doc = self.cast_to_document()
        if wait:
            add_to_db('problems', doc, replace=replace)
        else:
            add_to_db.delay('problems', doc, replace=replace)
        return self

    def delete(self, wait=False) -> None:
        if wait:
            delete_from_db('problems', self.cast_to_document())
        else:
            delete_from_db.delay('problems', self.cast_to_document())
    
    @classmethod
    def init(cls):
        for problem in cls.find_all():
            problem.update_num_solves()
