from config import *
from pymongo import MongoClient
from json import loads, dumps

db = MongoClient(MONGO_URI).tsoj

def migrate():
    submissions = db.submissions.find()
    for submission in submissions:
        submission['final_verdict'] = submission['final_verdict']['verdict']
        for result in submission['results']:
            result['verdict'] = result['verdict']['verdict']
        db.submissions.replace_one({'_id': submission['_id']}, submission)

if __name__ == '__main__':
    migrate()