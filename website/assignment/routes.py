from flask import Blueprint, render_template, abort
from website.models import Assignment

assignment_bp = Blueprint('assignment_bp', __name__,
                          template_folder='templates',
                          static_folder='static')

@assignment_bp.route('/<int:id>')
def assignment(id: int):
    # Hardcoded for now.
    assignment = Assignment.find_one({'id': id})
    if assignment is None:
        abort(404, description='Assignment not found')
    problems = assignment.fetch_problems()
    return render_template('assignment.html', assignment=assignment, problems=problems)
