from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user

from website.models import Submission
from isolate_wrapper import Verdict, Result

submission_bp = Blueprint('submission_bp', __name__, template_folder='templates', static_folder='static')

@submission_bp.route('/<int:id>')
@login_required
def submission(id: int) -> str:
    submission_obj = Submission.find_one({'id': id})
    if submission_obj is None:
        abort(404, description="Submission not found")
    show_code = current_user.is_admin or current_user.username == submission_obj.username or submission_obj.problem_id in current_user.get_solved_problem_ids()
    return render_template('submission.html', submission=submission_obj, show_code=show_code)
