from flask import render_template, Blueprint, request, redirect, url_for, flash, abort
from typing import List
from flask_login import login_required, current_user

from website.models import Problem, Assignment, Submission, User, UserGroup
from isolate_wrapper import Testcase
from website.celery_tasks import judge

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder='templates',
                     static_folder='static')


@admin_bp.before_request
@login_required
def unauthorised():
    if not current_user.is_admin:
        abort(403, description='Admin account required to access this page')


@admin_bp.route('/create/problem', methods=['GET', 'POST'])
def create_problem():
    if request.method == 'POST':
        problem_info = {
            'id': request.form['id'],
            'name': request.form['name'],
            'description': request.form['description'],
            'time_limit': int(round(float(request.form['time-limit']) * 1000)),
            'memory_limit': int(round(float(request.form['memory-limit']) * 1024)),
            'is_public': 'is_public' in request.form,
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
            'is_public': 'is_public' in request.form,
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


@admin_bp.route('/delete/problem/<id>')
def delete_problem(id: str):
    problem = Problem.find_one({'id': id})
    raise NotImplementedError
    problem.delete(wait=True)
    flash('Problem deleted', 'success')
    return redirect(url_for('home_bp.problems'))


@admin_bp.route('/create/assignment', methods=['GET', 'POST'])
def create_assignment():
    if request.method == 'POST':
        user_group_ids = [int(u_g_id) for u_g_id in request.form.get(
            'selected_user_group_ids').split(',')]
        new_assignment = Assignment(
            creator=current_user.username, user_group_ids=user_group_ids)
        problem_ids = request.form.get('selected_problem_ids').split(',')
        print(problem_ids)
        new_assignment.add_problems(*problem_ids)
        new_assignment.save(wait=True)

        flash('Assignment created', 'success')
        return redirect(url_for('admin_bp.assignments'))
    problems = Problem.find_all()
    user_groups = UserGroup.find_all()
    return render_template('create_assignment.html', problems=problems, user_groups=user_groups)


@admin_bp.route('/delete/assignment/<int:id>')
def delete_assignment(id: int):
    assignment = Assignment.find_one({'id': id})
    raise NotImplementedError
    assignment.delete(wait=True)
    flash('Assignment deleted', 'success')
    return redirect(url_for('admin_bp.assignments'))


@admin_bp.route('/assignments')
def assignments():
    all_assignments = Assignment.find_all(sort=True)
    user_group_names = {group.id: group.name for group in UserGroup.find_all()}
    return render_template('assignments.html', assignments=all_assignments, user_group_names=user_group_names)


@admin_bp.route('/assignment/<int:id>')  # /admin/assignment/id
def assignment_results(id: int):
    assignment = Assignment.find_one({'id': id})
    if assignment is None:
        abort(404, description='Assignment not found')
    problems = assignment.fetch_problems()
    user_groups = [UserGroup.find_one({'id': u_g_id})
                   for u_g_id in assignment.user_group_ids]
    users = {user.id: user for user in User.find_all()}
    solved_submissions = {}
    for user_id, user in users.items():
        solved_submissions[user_id] = [user.get_solved_submission(
            p_id) for p_id in assignment.problem_ids]
    return render_template('assignment_results.html', assignment=assignment, problems=problems, solved_submissions=solved_submissions, user_groups=user_groups, users=users)


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
    judge.delay(submission.code, submission.cast_to_document(),
                submission.problem_id)
    flash('Rejudging...')
    return redirect(url_for('submission_bp.submission', id=id))


@admin_bp.route('/user_groups')
def user_groups():
    user_groups = UserGroup.find_all()
    users = {user.id: user for user in User.find_all()}
    return render_template('user_groups.html', user_groups=user_groups, users=users)


@admin_bp.route('/create/user_group', methods=['GET', 'POST'])
def create_user_group():
    if request.method == 'POST':
        user_ids = request.form.get('selected_user_ids').split(',')
        user_group = UserGroup(name=request.form['name'],
                               user_ids=user_ids)
        user_group.save(wait=True)
        flash('Group created', 'success')
        return redirect(url_for('admin_bp.user_groups'))
    users = User.find_all()
    return render_template('create_user_group.html', users=users)


@admin_bp.route('/edit/user_group/<int:id>', methods=['GET', 'POST'])
def edit_user_group(id: int):
    if request.method == 'POST':
        user_ids = []
        users = User.find_all()
        for user in users:
            if f'is-in-group{user.id}' in request.form:
                user_ids.append(user.id)
        user_group = UserGroup(id=id,
                               name=request.form['name'],
                               user_ids=user_ids)
        user_group.save(replace=True)
        flash('Group saved', 'success')
        return redirect(url_for('admin_bp.user_groups'))
    user_group = UserGroup.find_one({'id': id})
    users = User.find_all()
    return render_template('edit_user_group.html', user_group=user_group, users=users)

@admin_bp.route('/delete/user_group/<int:id>')
def delete_user_group(id: int):
    user_group = UserGroup.find_one({'id': id})
    raise NotImplementedError
    user_group.delete(wait=True)
    flash('Group deleted', 'success')
    return redirect(url_for('admin_bp.user_groups'))


@admin_bp.route('/delete/submission/<int:id>')
def delete_submission(id: int):
    submission = Submission.find_one({'id': id})
    raise NotImplementedError
    submission.delete(wait=True)
    flash('Submission deleted', 'success')
    return redirect(url_for('home_bp.submissions'))
