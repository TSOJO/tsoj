from flask import render_template, Blueprint, request, redirect, url_for, flash, abort
from typing import List
from flask_login import login_required, current_user

from website.models import Problem, Assignment, Submission
from isolate_wrapper import IsolateSandbox, Verdict, Testcase

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder='templates',
                     static_folder='static')


@admin_bp.before_request
@login_required
def unauthorised():
    if not current_user.is_admin:
        abort(403)

@admin_bp.route('/')
def admin():
    return render_template('admin.html')


@admin_bp.route('/create/problem', methods=['GET', 'POST'])
def create_problem():
    if request.method == 'POST':
        # print(request.form)
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
            testcases.append(
                Testcase(request.form[f'input{i+1}'], request.form[f'answer{i+1}']))

        # if 'generator-checkbox' in request.form:
        #     code = request.form['generator-code']
        #     verdict: Verdict = IsolateSandbox().generate_answers(
        #         code, testcases, problem_info['time_limit'], problem_info['memory_limit'])[0]
        #     if not verdict.is_ac():
        #         raise NotImplementedError()

        problem = Problem(**problem_info, testcases=testcases)
        existing_problem = Problem.find_one({'id': problem.id})
        if existing_problem:
            flash(f'Problem with the id {problem.id} already exists.', 'error')
            return redirect(url_for('admin_bp.admin'))
        problem.save()

        flash('Problem created', 'success')
        # ? redirect to /problem/<id>/edit
        return redirect(url_for('problem_bp.problem_edit', id=problem.id))
    return render_template('create_problem.html')


@admin_bp.route('/create/assignment', methods=['GET', 'POST'])
def create_assignment():
    if request.method == 'POST':
        new_assignment = Assignment()
        # Only has problems.
        problems = request.form.to_dict().values()
        new_assignment.add_problems(*problems)
        new_assignment.save(wait=True)

        flash('Assignment created', 'success')
        # ? redirect to /assignments/ something something
        return redirect(url_for('admin_bp.admin'))
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
    print(submissions_dict)
    
    return render_template('assignment_results.html', assignment=assignment, problems=problems, submissions_dict=submissions_dict)
