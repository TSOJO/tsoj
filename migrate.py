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

if __name__ == '__main__':
    migrate()