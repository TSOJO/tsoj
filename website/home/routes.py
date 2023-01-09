from flask import Blueprint, render_template

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
    problems.sort(key=lambda p: p.id)
    return render_template('problems.html', problems=problems)

@home_bp.route('/submissions')
def submissions():
    submissions = Submission.find_all()
    submissions.sort(key=lambda s: s.id)
    return render_template('submissions.html', submissions=submissions)
