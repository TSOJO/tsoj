from flask import Blueprint, render_template, request, redirect, url_for, abort
from isolate_wrapper import IsolateSandbox, Testcase, Result, Verdict
from typing import List, Tuple
from website.celery_tasks import get_id_and_judge
from website.models import Problem
from website import app

problem_bp = Blueprint('problem_bp', __name__,
                       template_folder='templates',
                       static_folder='static')

# Load problem main screen.
@problem_bp.route('/<id>')
def problem(id: str) -> str:
    problem = Problem.find_one({'id': id})
    if problem is None:
        abort(404, description="Problem not found")
    assignment_id = request.args.get('assignment_id')
    return render_template('problem.html', problem=problem, assignment_id=assignment_id)

# Code submission.
@problem_bp.route('/<id>/submit', methods=['GET', 'POST'])
def problem_submit(id: str):
    # ! Harcoded
    username = 'john.doe'
    
    user_code = request.form.get('user_code')
    assignment_id = request.form.get('assignment_id')
    submission_id = get_id_and_judge(user_code=user_code, problem_id=id, username=username, assignment_id=assignment_id)
    return redirect(url_for('submission.submission', id=submission_id))
