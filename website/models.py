from . import db
import sqlalchemy as sa

class Problem(db.Model):
    id = sa.Column(sa.String(10), primary_key=True)
    title = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String(5000), nullable=False)
    
    def __repr__(self):
        return f'<Problem {self.id}>'
