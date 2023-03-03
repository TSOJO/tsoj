from config import *
from pymongo import MongoClient

db = MongoClient(MONGO_URI).tsoj

def migrate():
    submissions = db.submissions.find()
    for submission in submissions:
        try:
            db.problems.find_one({'id': submission['problem_id']})
        except:
            db.submissions.delete_one({'id': submission['id']})

if __name__ == '__main__':
    migrate()