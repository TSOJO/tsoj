from flask import render_template, Blueprint, request
from . import db
from .models import Problem

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/')
def admin():
    return render_template('admin.html')

@admin_bp.route('/create_problem', methods=['GET', 'POST'])
def create_problem():
    if request.method == 'POST':
        print(request.form['input[]'])
        # problem_info = {
        #     'id': request.form['id'],
        #     'title': request.form['title'],
        #     'description': request.form['description'],
        # }
        # p = Problem(**problem_info)
        # db.session.add(p)
        # db.session.commit()
        # return redirect(url_for('admin_bp.admin'))
    return render_template('create_problem.html')

@admin_bp.route('/create_prep')
def create_prep():
    return render_template('create_prep.html')