from config import *
from pymongo import MongoClient
from json import loads, dumps

db = MongoClient(MONGO_URI).tsoj

def migrate():
    problems = db.problems.find()
    for problem in problems:
        problem['generate_input_code'] = None
        problem['generate_answer_code'] = None
        db.problems.replace_one({'_id': problem['_id']}, problem)

if __name__ == '__main__':
    migrate()