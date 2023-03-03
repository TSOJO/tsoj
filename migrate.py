from config import *
from pymongo import MongoClient

db = MongoClient(MONGO_URI).tsoj

def migrate():
    submissions = db.submissions.find()
    for submission in submissions:
        problem = db.problems.find_one({'id': submission['problem_id']})
        if problem is None:
            db.submissions.delete_one({'id': submission['id']})

if __name__ == '__main__':
    migrate()