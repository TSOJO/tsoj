from flask import Blueprint, render_template

from website.models import Problem

home_bp = Blueprint('home_bp', __name__,
                    template_folder='templates',
                    static_folder='static')

@home_bp.route('/')
def home():
    return render_template('home.html')

@home_bp.route('/problems/')
async def problems():
    problems_list = await Problem.find_all()
    print(problems_list)
    return render_template('problems.html', problems=problems_list)
