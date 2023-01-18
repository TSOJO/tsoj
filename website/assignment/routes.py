from flask import render_template, Blueprint, request, redirect, url_for, flash, abort
from website.models import Assignment
from flask_login import current_user

assignment_bp = Blueprint(
    'assignment_bp', __name__, template_folder='templates', static_folder='static'
)


@assignment_bp.route('/<int:id>')
def assignment(id: int):
    assignment_obj = Assignment.find_one(filter={'id': id})
    if assignment_obj is None:
        abort(404, description='Assignment not found')
    for user_group in current_user.user_group_ids:
        if user_group in assignment_obj.user_group_ids:
            solved_problems = current_user.get_solved_problem_ids()
            problems = assignment_obj.fetch_problems()
            return render_template(
                'assignment.html',
                assignment=assignment_obj,
                solved_problems=solved_problems,
                problems=problems,
            )
    abort(403, description='You are not allowed to view this assignment')
