from flask import Blueprint, render_template

assignment_bp = Blueprint('assignment_bp', __name__,
                          template_folder='templates',
                          static_folder='static')

@assignment_bp.route('/<int:id>')
def assignment(id: int):
    # Hardcoded for now.
    assignment_obj = {
        'id': 1,
        'problems': [
            {
                'id': 'A1',
                'title': 'Sum',
                'description': 'Given two numbers, print their sum.',
            },
            {
                'id': 'A2',
                'title': 'Difference',
                'description': 'Given two numbers, print their difference.',
            }
        ]
    }
    return render_template('assignment.html', assignment=assignment_obj)
