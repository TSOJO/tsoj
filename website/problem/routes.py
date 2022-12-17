from flask import Blueprint, render_template, request, redirect, url_for
from isolate_wrapper import IsolateSandbox, Testcase, Result, Verdict
from typing import List, Tuple
from website.celery_tasks import judge
from website.models import Problem
from website import app

problem_bp = Blueprint('problem_bp', __name__,
                       template_folder='templates',
                       static_folder='static')

# Load problem main screen.
@problem_bp.route('/<id>')
def problem(id: str) -> str:
    problem = Problem.find_one({'id': id})
    assignment_id = request.args.get('assignment_id')
    return render_template('problem.html', problem=problem, assignment_id=assignment_id)

# Code submission.
@problem_bp.route('/<id>/submit', methods=['GET', 'POST'])
def problem_submit(id: str):
    # TODO: After submission, the whole result should be stored into a database, and should redirect to /submission/<submission-id> instead.
    # ? Maybe should look like:
    # ? Submit code --(POST)--> /submit (judge + add to DB) --(redirect with submission ID)--> /submission/<id>
    # ! Harcoded
    username = 'john.doe'
    
    user_code = request.form.get('user_code')
    # TODO: Assignment ID in problem page
    assignment_id = request.form.get('assignment_id', default=None)
    judge.delay(user_code, id, username, assignment_id)
    return redirect(url_for('submission.submission'))
    # final_verdict, results = judge(user_code, testcases, 1, 1024*64)
    # return render_template('results.html',
    #                        problem=problem_info,
    #                        final_verdict=final_verdict,
    #                        results=results)
