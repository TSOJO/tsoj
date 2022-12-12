from flask import Blueprint, render_template

from website.models import Problem

home_bp = Blueprint('home_bp', __name__,
                    static_url_path='/home/static',  # Because url prefix is '/'
                    template_folder='templates',
                    static_folder='static')

@home_bp.route('/')
def home():
    return render_template('home.html')

@home_bp.route('/problems/')
def problems():
    problems = Problem.find_all()
    return render_template('problems.html', problems=problems)
