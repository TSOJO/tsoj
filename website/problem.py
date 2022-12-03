from flask import Blueprint, render_template, request
from ..isolate_wrapper import IsolateSandbox
problem_bp = Blueprint('problem_bp', __name__)

# Load problem main screen.
@problem_bp.route('/<int:id>')
def problem(id: int) -> str:
    
    # This is hardcoded for development purposes.
    # `problem` in production will be an object from the problem database.
    # No type is defined here as the type will be inferred from the database model we create later.
    problem_info = {
        'id': 1,
        'title': 'Sum',
        'description': 'Given two numbers, print their sum.',
    }
    return render_template('problem.html', problem=problem_info)

# Code submission.
@problem_bp.route('/submit', methods=['POST'])
def problem_submit() -> str:
    # TODO: Make sandbox run asynchronously.
    user_code = request.form['user_code']
    sandbox = IsolateSandbox(0)
    sandbox.run_code(user_code)
    return "OK"
