from config import *
from pymongo import MongoClient
from json import loads, dumps

db = MongoClient(MONGO_URI).tsoj

def migrate():
    problems = db.problems.find()
    for problem in problems:
        old = problem['_id']
        problem['_id'] = problem['id'].replace('NTRO', 'ntro')
        problem['id'] = problem['id'].replace('NTRO', 'ntro')
        db.problems.replace_one({'_id': old}, problem)

    for submission in db.submissions.find():
        submission['problem_id'] = submission['problem_id'].replace('NTRO', 'ntro')
        db.submissions.replace_one({'_id': old}, submission)

if __name__ == '__main__':
    migrate()