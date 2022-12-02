from flask import Blueprint, render_template, request
from isolate_wrapper import IsolateSandbox
problem_bp = Blueprint('problem_bp', __name__)

# Load problem main screen.
@problem_bp.route('/<int:id>')
def problem(id):
    
    # This is hardcoded for development purposes.
    # `problem` in production will be an object from the problem database.
    problem_dict = {
        'id': 1,
        'title': 'Sum',
        'description': 'Given two numbers, print their sum.',
    }
    
    return render_template('problem.html', problem=problem_dict)

# Code submission.
@problem_bp.route('/submit', methods=['POST'])
def problem_submit():
    #TODO: make sandbox run asynchronously.
    user_code = request.form['user_code']
    sandbox = IsolateSandbox(0)
    sandbox.run_code(user_code)
    return "OK"
