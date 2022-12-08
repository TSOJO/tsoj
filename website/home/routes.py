from flask import Blueprint, render_template

home_bp = Blueprint('home_bp', __name__, template_folder='templates', static_folder='static')

@home_bp.route('/')
def home():
    return render_template('home.html')

@home_bp.route('/problems')
def problems():
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