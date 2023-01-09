from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from typing import List
from flask_login import login_required, current_user

from website.celery_tasks import judge
from website.models import Problem, Submission
from isolate_wrapper import Testcase


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

@problem_bp.route('/<id>/submit', methods=['POST'])
@login_required
def problem_submit(id: str):
    username = current_user.username

    user_code = request.form.get('user_code')
    assignment_id = request.form.get('assignment_id')
    if assignment_id:
        assignment_id = int(assignment_id)
    new_submission = Submission(username=username,
                                problem_id=id,
                                code=user_code,
                                assignment_id=assignment_id)
    submission_id = new_submission.save(wait=True).id
    judge.delay(user_code=user_code,
                submission_dict=new_submission.cast_to_document(),
                problem_id=id,)
    return redirect(url_for('submission_bp.submission', id=submission_id))

@problem_bp.route('/<id>/edit', methods=['GET', 'POST'])
def problem_edit(id: str):
    if request.method == 'POST':
        problem_info = {
            'id': request.form['id'],
            'name': request.form['name'],
            'description': request.form['description'],
            'time_limit': int(round(float(request.form['time-limit']) * 1000)),
            'memory_limit': int(round(float(request.form['memory-limit']) * 1024)),
        }
        testcases: List[Testcase] = []

        testcases_count = int(request.form['testcases-count'])
        for i in range(testcases_count):
            testcases.append(
                Testcase(request.form[f'input{i+1}'], request.form[f'answer{i+1}']))

        # if 'generator-checkbox' in request.form:
        #     code = request.form['generator-code']
        #     verdict: Verdict = IsolateSandbox().generate_answers(
        #         code, testcases, problem_info['time_limit'], problem_info['memory_limit'])[0]
        #     if not verdict.is_ac():
        #         raise NotImplementedError()

        problem = Problem(**problem_info, testcases=testcases)
        problem.save(replace=True)

        flash('Problem saved', 'success')
        return redirect(url_for('problem_bp.problem', id=problem.id))
    problem = Problem.find_one({'id': id})
    return render_template('problem_edit.html', problem=problem)