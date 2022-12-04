from flask import Blueprint, render_template, request
from isolate_wrapper import IsolateSandbox

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
@problem_bp.route('/results', methods=['GET', 'POST'])
def problem_results() -> str:
    # TODO: After submission, the whole result should be stored into a database, and should redirect to /submission/<submission-id> instead.
    # Maybe should look like:
    # Submit code --(POST)--> /submit (judge + add to DB) --(redirect with submission ID)--> /submission/<id>
    # ??

    # Note this is hardcoded for development.
    # Probably get this from `problem_id` in production.
    testcases = [
        {
            'id': 1,
            'input': '2\n9\n',
            'answer': '11',
        },
        {
            'id': 2,
            'input': '10\n20\n',
            'answer': '30',
        }
    ]
    
    restrictions = {
        'time_limit': 1,
        'memory_limit': 1024*64,
    }
    
    problem_info = {
        'id': 1,
        'title': 'Sum',
        'description': 'Given two numbers, print their sum.',
    }
    
    user_code = request.form['user_code']
    problem_id = request.form['problem_id']
    sandbox = IsolateSandbox()
    final_verdict, results = sandbox.run_code(user_code, testcases, restrictions)
    print(final_verdict, results)
    return render_template('results.html',
                           problem=problem_info,
                           final_verdict=final_verdict,
                           results=results)
