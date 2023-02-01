from flask import Blueprint, render_template, request, abort
from flask_login import current_user

from website.models import Submission, User, Problem

submission_bp = Blueprint(
    'submission_bp', __name__, template_folder='templates', static_folder='static'
)


@submission_bp.route('/<int:id>')
def submission(id: int) -> str:
    submission_obj = Submission.find_one({'id': id})
    if submission_obj is None:
        abort(404, description="Submission not found")
    user_obj = User.find_one({'id': submission_obj.user_id})
    problem_obj = Problem.find_one({'id': submission_obj.problem_id})
    if not current_user.is_contributor() and not problem_obj.is_public:
        abort(403, 'Problem is not public')
    show_code = (
        current_user.is_admin()
        or current_user.id == submission_obj.user_id
        or submission_obj.problem_id in current_user.get_solved_problem_ids()
    )
    return render_template(
        'submission.html',
        submission=submission_obj,
        submission_user=user_obj,
        show_code=show_code,
    )
