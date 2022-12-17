from flask import Blueprint, render_template, request, redirect, url_for, flash

from website.models import Submission
from isolate_wrapper import Verdict, Result

submission_bp = Blueprint('submission', __name__, template_folder='templates', static_folder='static')

@submission_bp.route('/<id>')
def submission(id: int) -> str:
    submission: Submission = Submission(
        username='fuco1',
        final_verdict=Verdict.AC,
        results=[
            Result(Verdict.AC, 400, 64*1024),
            Result(Verdict.AC, 390, 64*1024),
        ],
        problem_id='A1',
        assignment_id=1,
    )
    return render_template('submission.html', submission=submission)
