from . import db

class Problem(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
