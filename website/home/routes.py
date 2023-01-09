from flask import Blueprint, render_template, request

from website.models import Problem, Submission

home_bp = Blueprint('home_bp', __name__,
                    static_url_path='/home/static',  # Because url prefix is '/'
                    template_folder='templates',
                    static_folder='static')


@home_bp.route('/')
def home():
    return render_template('home.html')

# require trailing slash for some reason


@home_bp.route('/problems/')
def problems():
    problems = Problem.find_all()
    return render_template('problems.html', problems=problems)


@home_bp.route('/submissions')
def submissions():
    filter = {}
    user_id = request.args.get('id')
    problem_id = request.args.get('problem_id')
    if user_id is not None:
        filter['id'] = user_id
    if problem_id is not None:
        filter['problem_id'] = problem_id
    submissions = Submission.find_all(filter=filter)
    return render_template('submissions.html', submissions=submissions)
