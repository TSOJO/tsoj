from flask import render_template, Blueprint, request, redirect, url_for, flash, abort
from typing import List
from flask_login import login_required, current_user

from website.models import Problem, Assignment, Submission, User, UserGroup
from isolate_wrapper import Testcase, Language, SourceCode
from website.celery_tasks import judge
from website.utils import to_input_format

admin_bp = Blueprint(
    'admin_bp', __name__, template_folder='templates', static_folder='static'
)


@admin_bp.before_request
@login_required
def unauthorised():
    allowed_endpoints_for_contributors = [
        'admin_bp.create_problem',
        'admin_bp.edit_problem',
        'admin_bp.delete_problem',
        'admin_bp.rejudge_submission',
    ]
    if current_user.is_admin():
        return
    if current_user.is_contributor() and request.endpoint in allowed_endpoints_for_contributors:
        return
    abort(403, description='Admin or contributor prvileges are required to access this page')



# Problem


@admin_bp.route('/create/problem', methods=['POST'])
def create_problem():
    problem = Problem(
        id=request.form['problem_id'],
        name='',
        description='''
Enter description

##### Input
Enter input format

##### Output
Enter output format

##### Constraints
Enter input constraints''',
        hints=[],
        time_limit=1000,
        memory_limit=64*1024,
        is_public=False,
        allowed_languages=list(Language),
        testcases=[Testcase(input='', answer='')]
    )
    problem.save(wait=True)
    flash('Problem created', 'success')
    return redirect(url_for('admin_bp.edit_problem', id=problem.id))

@admin_bp.route('/edit/problem/<id>', methods=['GET', 'POST'])
def edit_problem(id: str):
    if request.method == 'POST':
        problem_info = {
            'id': id,
            'name': request.form['name'],
            'description': request.form['description'],
            'hints': [hint.strip() for hint in request.form['hints'].split('\n') if hint.strip() != ''],
            'time_limit': int(round(float(request.form['time-limit']) * 1000)),
            'memory_limit': int(round(float(request.form['memory-limit']) * 1024)),
            'is_public': 'is_public' in request.form,
            'aqaasm_inputs': [address.strip() for address in request.form['input-address'].split('\n') if address.strip() != ''],
            'aqaasm_outputs': [address.strip() for address in request.form['output-address'].split('\n') if address.strip() != ''],
        }

        testcases: List[Testcase] = []
        testcases_count = int(request.form['testcases-count'])
        for i in range(testcases_count):
            example = f'example{i}' in request.form
            testcases.append(
                Testcase(
                    to_input_format(request.form[f'input{i}']),
                    request.form[f'answer{i}'],
                    0 if example else 1,
                )
            )

        judge_method = request.form.get('judge-method')
        if judge_method == 'grader':
            grader_code = request.form['grader-code']
            grader_language = Language.cast_from_document(request.form['grader-language'])
            problem_info['grader_source_code'] = SourceCode(grader_code, grader_language)
        
        if 'restrict-langs' in request.form:
            allowed_languages = [Language.cast_from_document(lang) for lang in request.form.getlist('allowed-languages')]
        else:
            allowed_languages = None

        problem = Problem(**problem_info, testcases=testcases, allowed_languages=allowed_languages)
        problem.save(replace=True, wait=True)

        if 'rejudge' in request.form:
            _rejudge_problem(problem.id)
        flash('Problem saved', 'success')
        return redirect(url_for('problem_bp.problem', id=problem.id))
    problem = Problem.find_one({'id': id})
    return render_template('edit_problem.html', problem=problem, all_languages=list(Language))


@admin_bp.route('/delete/problem/<id>')
def delete_problem(id: str):
    problem = Problem.find_one({'id': id})
    problem.delete(wait=True)
    for submission in Submission.find_all({'problem_id': id}):
        submission.delete(wait=True)
    flash('Problem deleted', 'success')
    return redirect(url_for('home_bp.problems'))


# Assignment


@admin_bp.route('/assignments')
def assignments():
    all_assignments = Assignment.find_all(sort=True)
    user_group_names = {group.id: group.name for group in UserGroup.find_all()}
    return render_template(
        'assignments.html',
        assignments=all_assignments,
        user_group_names=user_group_names,
    )


@admin_bp.route('/assignment/<int:id>')  # /admin/assignment/id
def assignment_results(id: int):
    assignment = Assignment.find_one({'id': id})
    if assignment is None:
        abort(404, description='Assignment not found')
    problems = assignment.fetch_problems()
    user_groups = [
        UserGroup.find_one({'id': u_g_id}) for u_g_id in assignment.user_group_ids
    ]
    user_dict = {}  # {user_id: user object}
    for user_group in user_groups:
        for user_id in user_group.user_ids:
            user_dict[user_id] = User.find_one({'id': user_id})

    assignment_submissions = {user_id: user.get_assignment_submissions(assignment) for user_id, user in user_dict.items()}
    return render_template(
        'assignment_results.html',
        assignment=assignment,
        problems=problems,
        assignment_submissions=assignment_submissions,
        user_groups=user_groups,
        users=user_dict,
    )


@admin_bp.route('/edit/assignment/<int:id>', methods=['GET', 'POST'])
def edit_assignment(id: int):
    if request.method == 'POST':
        # JS guarantees there is at least one user group and one problem selected.
        user_group_ids = [
            int(u_g_id)
            for u_g_id in request.form.get('selected_user_group_ids').split(',')
        ]
        problem_ids = request.form.get('selected_problem_ids').split(',')

        new_assignment = Assignment(
            creator=current_user.username, user_group_ids=user_group_ids
        )
        new_assignment.add_problems(*problem_ids)
        new_assignment.save(wait=True)

        flash('Assignment created', 'success')
        return redirect(url_for('admin_bp.assignments'))
    assignment = Assignment.find_one({'id': id})
    problems = Problem.find_all()
    user_groups = UserGroup.find_all()
    return render_template(
        'edit_assignment.html', problems=problems, user_groups=user_groups, assignment=assignment
    )

@admin_bp.route('/delete/assignment/<int:id>')
def delete_assignment(id: int):
    assignment = Assignment.find_one({'id': id})
    assignment.delete(wait=True)
    flash('Assignment deleted', 'success')
    return redirect(url_for('admin_bp.assignments'))


# Rejudge


def _rejudge_problem(id: str):
    problem = Problem.find_one({'id': id})
    if problem is None:
        flash(f'Unable to rejudge problem {id}: problem not found.', 'error')
        return
    submissions = Submission.find_all({'problem_id': id})
    grader_source_code_dict = problem.grader_source_code.cast_to_document() if problem.grader_source_code is not None else None
    for submission in submissions:
        judge.delay(submission.code, submission.language.cast_to_document(), submission.cast_to_document(), id, grader_source_code_dict)
    flash(f'Rejudging all submissions to problem {id}...')


@admin_bp.route('/rejudge/submission/<int:id>')
def rejudge_submission(id: int):
    submission = Submission.find_one({'id': id})
    if submission is None:
        abort(404, description="Submission not found")
    problem = Problem.find_one({'id': submission.problem_id})
    if problem is None:
        flash(f'Unable to rejudge submission {id}: problem not found.', 'error')
        return redirect(url_for('submission_bp.submission', id=id))
    submission.create_empty_results(len(problem.testcases))
    submission.save(replace=True, wait=True)
    grader_source_code_dict = problem.grader_source_code.cast_to_document() if problem.grader_source_code is not None else None
    judge.delay(submission.code, submission.language.cast_to_document(), submission.cast_to_document(), submission.problem_id, grader_source_code_dict)
    flash('Rejudging...')
    return redirect(url_for('submission_bp.submission', id=id))


# User group


@admin_bp.route('/groups')
def user_groups():
    user_groups = UserGroup.find_all()
    users = {user.id: user for user in User.find_all()}
    return render_template('user_groups.html', user_groups=user_groups, users=users)


@admin_bp.route('/create/group', methods=['POST'])
def create_user_group():
    user_group = UserGroup(name=request.form['group_name'])
    user_group.save(wait=True)
    flash('Group created', 'success')
    return redirect(url_for('admin_bp.edit_user_group', id=user_group.id))


@admin_bp.route('/edit/group/<int:id>', methods=['GET', 'POST'])
def edit_user_group(id: int):
    if request.method == 'POST':
        user_ids_raw = request.form.get('selected_user_ids')
        user_group = UserGroup.find_one({'id': id})
        if user_ids_raw:
            user_ids = user_ids_raw.split(',')
            user_group.user_ids = user_ids
        user_group.save(replace=True, wait=True)
        flash('Group saved', 'success')
        return redirect(url_for('admin_bp.user_groups'))
    user_group = UserGroup.find_one({'id': id})
    users = User.find_all()
    return render_template('edit_user_group.html', user_group=user_group, users=users)


@admin_bp.route('/delete/group/<int:id>')
def delete_user_group(id: int):
    user_group = UserGroup.find_one({'id': id})
    user_group.delete(wait=True)
    flash('Group deleted', 'success')
    return redirect(url_for('admin_bp.user_groups'))

# Other

@admin_bp.route('/delete/submission/<int:id>')
def delete_submission(id: int):
    submission = Submission.find_one({'id': id})
    submission.delete(wait=True)
    flash('Submission deleted', 'success')
    return redirect(url_for('home_bp.submissions'))

@admin_bp.route('/edit/privileges', methods=['GET', 'POST'])
def edit_privileges():
    users = User.find_all()
    if request.method == 'POST':
        for user in users:
            new_privilege = int(request.form.get(f'privilege{user.id}'))
            if user == current_user and new_privilege != user.privilege:
                flash('You cannot change your own privileges!', 'error')
                continue
            if new_privilege != user.privilege:
                user.privilege = new_privilege
                user.save(replace=True, wait=True)
        flash('Privileges saved', 'success')
    return render_template('edit_privileges.html', users=users)