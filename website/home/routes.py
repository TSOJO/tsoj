from flask import Blueprint, render_template, request
from flask_login import current_user
from typing import *

from website.models import Problem, Submission, User, Assignment

home_bp = Blueprint(
    'home_bp',
    __name__,
    static_url_path='/home/static',  # Because url prefix is '/'
    template_folder='templates',
    static_folder='static',
)


@home_bp.route('/')
def home():
    assignments: List[Assignment] = current_user.fetch_assignments(sort=True)
    problems = {}
    finished_assignment_ids = []
    solved_problem_ids = current_user.get_solved_problem_ids()
    for assignment in assignments:
        problems[assignment.id] = assignment.fetch_problems()
        if all(pid in solved_problem_ids for pid in assignment.problem_ids):
            finished_assignment_ids.append(assignment.id)
    return render_template('home.html', assignments=assignments, problems=problems, finished_assignment_ids=finished_assignment_ids, solved_problem_ids=solved_problem_ids)


@home_bp.route('/problems/')  # ? require trailing slash for some reason
def problems():
    problems = Problem.find_all()
    solved_problems = current_user.get_solved_problem_ids()
    return render_template(
        'problems.html', problems=problems, solved_problems=solved_problems
    )


@home_bp.route('/submissions')
def submissions():
    filter = {}
    user_id = request.args.get('id')
    problem_id = request.args.get('problem_id')
    if user_id is not None:
        filter['id'] = user_id
    if problem_id is not None:
        filter['problem_id'] = problem_id
    submissions = Submission.find_all(filter=filter, sort=True)
    users = dict(map(lambda u: (u.id, u), User.find_all()))
    problems = dict(map(lambda p: (p.id, p), Problem.find_all()))
    return render_template(
        'submissions.html', submissions=submissions, users=users, problems=problems
    )

@home_bp.route('/guide')
def guide():
    return render_template('guide.html')

@home_bp.route('/contributor_guide')
def contributor_guide():
    return render_template('contributor_guide.html')

