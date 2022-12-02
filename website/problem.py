from flask import Blueprint, render_template

problem_bp = Blueprint('problem_bp', __name__)

@problem_bp.route('/<int:id>')
def problem(id):
    return render_template('problem.html', problem_id=id)
