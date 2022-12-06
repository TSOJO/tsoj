from flask import render_template, Blueprint
# from . import db
# from .models import Problem

# Blueprint Configuration
problems_bp = Blueprint('home_bp', __name__)

@problems_bp.route('/')
def problems():
    # problems_list = db.session.query(Problem).all()
    problems_list = [
        {
            'id': 'A1',
            'title': 'Sum',
            'description': 'Given two numbers, print their sum.',
        },
        {
            'id': 'A2',
            'title': 'Difference',
            'description': 'Given two numbers, print their difference.',
        }
    ]
    return render_template('problems.html', problems=problems_list)