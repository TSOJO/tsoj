from flask import render_template, Blueprint
from . import db
from .models import Problem

# Blueprint Configuration
problems_bp = Blueprint('home_bp', __name__)

@problems_bp.route('/')
def problems():
    print('test')
    problems_list = db.session.query(Problem).all()
    return render_template('problems.html', problems=problems_list)
