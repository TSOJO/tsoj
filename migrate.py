from config import *
from pymongo import MongoClient

db = MongoClient(MONGO_URI).tsoj

def migrate():
    problems = db.problems.find()
    for problem in problems:
        problem['aqaasm_inputs'] = []
        problem['aqaasm_outputs'] = []
        db.problems.replace_one({'_id': problem['_id']}, problem)

if __name__ == '__main__':
    migrate()