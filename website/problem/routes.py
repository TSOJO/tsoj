from flask import Blueprint, render_template, request, redirect
from isolate_wrapper import IsolateSandbox, Testcase, Result, Verdict
from typing import List, Tuple
from website.celery_tasks import judge

problem_bp = Blueprint('problem_bp', __name__,
                       template_folder='templates',
                       static_folder='static')

# Load problem main screen.
@problem_bp.route('/<id>')
def problem(id: str) -> str:
    # Hardcoded for now.
    problem_info = {
        'id': 'A1',
        'title': 'Sum',
        'description': 'Given two numbers, print their sum.',
    }
    assignment_id = request.args.get('assignment_id')
    return render_template('problem.html', problem=problem_info, assignment_id=assignment_id)

# Code submission.
@problem_bp.route('/submit', methods=['GET', 'POST'])
def problem_submit() -> str:
    # TODO: Remove hardcoded problem id.
    # TODO: After submission, the whole result should be stored into a database, and should redirect to /submission/<submission-id> instead.
    # ? Maybe should look like:
    # ? Submit code --(POST)--> /submit (judge + add to DB) --(redirect with submission ID)--> /submission/<id>

    # Note this is hardcoded for development.
    # Probably get this from `problem_id` in production.
    
    user_code = request.form['user_code']
    problem_id = request.form['problem_id']
    # final_verdict, results = judge(user_code, testcases, 1, 1024*64)
    task = judge.delay(user_code, problem_id)
    return redirect('/')
    # return render_template('results.html',
    #                        problem=problem_info,
    #                        final_verdict=final_verdict,
    #                        results=results)
