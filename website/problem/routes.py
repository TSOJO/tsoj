from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from typing import List
from flask_login import current_user

from website.celery_tasks import judge
from website.models import Problem, Submission
from isolate_wrapper import Testcase


problem_bp = Blueprint(
    'problem_bp', __name__, template_folder='templates', static_folder='static'
)


@problem_bp.route('/<id>')
def problem(id: str) -> str:
    problem = Problem.find_one({'id': id})
    if problem is None:
        abort(404, description="Problem not found")
    if not current_user.is_admin and not problem.is_public:
        abort(400, 'Unauthorized')
    assignment_id = request.args.get('assignment_id')
    return render_template('problem.html', problem=problem, assignment_id=assignment_id)


@problem_bp.route('/<id>/submit', methods=['POST'])
def problem_submit(id: str):
    user_id = current_user.id

    user_code = request.form.get('user_code')
    new_submission = Submission(user_id=user_id, problem_id=id, code=user_code)
    submission_id = new_submission.save(wait=True).id
    judge.delay(
        user_code=user_code,
        submission_dict=new_submission.cast_to_document(),
        problem_id=id,
    )
    return redirect(url_for('submission_bp.submission', id=submission_id))
