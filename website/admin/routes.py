from flask import render_template, Blueprint, request, redirect, url_for, flash, abort
from typing import List
from flask_login import login_required, current_user

from website.models import Problem, Assignment, Submission, User
from isolate_wrapper import IsolateSandbox, Verdict, Testcase
from website.celery_tasks import judge

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder='templates',
                     static_folder='static')


@admin_bp.before_request
@login_required
def unauthorised():
    if not current_user.is_admin:
        abort(403, description='Admin account required to access this page')

@admin_bp.route('/')
def admin():
    return render_template('admin.html')


@admin_bp.route('/create/problem', methods=['GET', 'POST'])
def create_problem():
    if request.method == 'POST':
        problem_info = {
            'id': request.form['id'],
            'name': request.form['name'],
            'description': request.form['description'],
            'time_limit': int(round(float(request.form['time-limit']) * 1000)),
            'memory_limit': int(round(float(request.form['memory-limit']) * 1024)),
        }
        testcases: List[Testcase] = []

        testcases_count = int(request.form['testcases-count'])
        for i in range(testcases_count):
            sample = f'sample{i+1}' in request.form
            testcases.append(
                Testcase(request.form[f'input{i+1}'], request.form[f'answer{i+1}'], 0 if sample else 1))

        problem = Problem(**problem_info, testcases=testcases)
        problem.save(wait=True)

        flash('Problem created', 'success')
        return redirect(url_for('problem_bp.problem', id=problem.id))
    return render_template('create_problem.html')

@admin_bp.route('/edit/problem/<id>', methods=['GET', 'POST'])
def edit_problem(id: str):
    if request.method == 'POST':
        problem_info = {
            'id': id,
            'name': request.form['name'],
            'description': request.form['description'],
            'time_limit': int(round(float(request.form['time-limit']) * 1000)),
            'memory_limit': int(round(float(request.form['memory-limit']) * 1024)),
        }
        testcases: List[Testcase] = []

        testcases_count = int(request.form['testcases-count'])
        for i in range(testcases_count):
            sample = f'sample{i+1}' in request.form
            testcases.append(
                Testcase(request.form[f'input{i+1}'], request.form[f'answer{i+1}'], 0 if sample else 1))

        problem = Problem(**problem_info, testcases=testcases)
        problem.save(replace=True)

        flash('Problem saved', 'success')
        return redirect(url_for('problem_bp.problem', id=problem.id))
    problem = Problem.find_one({'id': id})
    return render_template('edit_problem.html', problem=problem)


@admin_bp.route('/create/assignment', methods=['GET', 'POST'])
def create_assignment():
    if request.method == 'POST':
        print(request.form.get('selected_ids').split(','))
        new_assignment = Assignment(creator=current_user.username)
        problem_ids = request.form.get('selected_ids').split(',')
        new_assignment.add_problems(*problem_ids)
        new_assignment.save(wait=True)

        flash('Assignment created', 'success')
        return redirect(url_for('assignment_bp.assignment', id=new_assignment.id))
    problems = Problem.find_all()
    return render_template('create_assignment.html', problems=problems)

@admin_bp.route('/assignments')
def assignments():
    all_assignments = Assignment.find_all(sort=True)
    return render_template('assignments.html', assignments=all_assignments)

@admin_bp.route('/assignment/<int:id>')  # /admin/assignment/id
def assignment_results(id: int):
    assignment = Assignment.find_one({'id': id})
    if assignment is None:
        abort(404, description='Assignment not found')
    problems = assignment.fetch_problems()
    
    submissions = Submission.find_all({'assignment_id': id}, sort=True)
    submissions_dict = {}  # {problem id: [list of submissions to that problem]}
    for submission in submissions:
        if submission.problem_id not in submissions_dict:
            submissions_dict[submission.problem_id] = []
        submissions_dict[submission.problem_id].append(submission)
    
    full_names = dict(map(lambda u: (u.id, u.full_name), User.find_all()))
    return render_template('assignment_results.html', assignment=assignment, problems=problems, submissions_dict=submissions_dict, full_names=full_names)

@admin_bp.route('/rejudge/problem/<id>')
def rejudge_problem(id: str):
    problem = Problem.find_one({'id': id})
    if problem is None:
        abort(404, description="Problem not found.")
    submissions = Submission.find_all({'problem_id': id})
    for submission in submissions:
        judge.delay(submission.code, submission.cast_to_document(), id)
    flash(f'Rejudging all submissions with problem ID {id}...')
    return redirect(url_for('home_bp.submissions', problem_id=id))

@admin_bp.route('/rejudge/submission/<int:id>')
def rejudge_submission(id: int):
    submission = Submission.find_one({'id': id})
    if submission is None:
        abort(404, description="Submission not found")
    judge.delay(submission.code, submission.cast_to_document(), submission.problem_id)
    flash('Rejudging...')
    return redirect(url_for('submission_bp.submission', id=id))
