from flask import Blueprint, render_template, request, abort

from website.models import Submission
from isolate_wrapper import Verdict, Result

submission_bp = Blueprint('submission_bp', __name__, template_folder='templates', static_folder='static')

@submission_bp.route('/<int:id>')
def submission(id: int) -> str:
    submission_obj = Submission.find_one({'id': id})
    if submission_obj is None:
        abort(404, description="Submission not found")
    return render_template('submission.html', submission=submission_obj)
