from flask import render_template, Blueprint, request, redirect, url_for, flash, abort, current_app as app
from typing import List
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import zipfile
import shutil
import logging

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
        'admin_bp.static',
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
        id=request.form['problem-id'],
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
        if 'generate-input' in request.form:
            generate_input_code = request.form['input-generator-code']
            generate_input_language = Language.cast_from_document(request.form['input-generator-language'])
            problem_info['generate_input_code'] = SourceCode(generate_input_code, generate_input_language)
        if 'generate-answer' in request.form:
            generate_answer_code = request.form['generator-code']
            generate_answer_language = Language.cast_from_document(request.form['answer-generator-language'])
            problem_info['generate_answer_code'] = SourceCode(generate_answer_code, generate_answer_language)

        testcase_type = request.form['testcase-type']
        if testcase_type == 'manual':
            testcases: List[Testcase] = []
            testcases_count = int(request.form['testcases-count'])
            for i in range(testcases_count):
                example = f'example{i}' in request.form
                testcases.append(
                    Testcase(
                        to_input_format(request.form[f'input{i}']),
                        request.form[f'answer{i}'],
                        0 if example else int(request.form[f'batch_number{i}']),
                    )
                )
            problem_info['testcases'] = testcases
        elif testcase_type == 'file':
            problem_info['testcase_from_file'] = True
            testcases = []
            testcase_file = request.files['testcase-file']
            if testcase_file.filename == '': # no file selected
                if f'{id}.zip' not in os.listdir(app.config['UPLOADS_PATH']):
                    flash('No testcase file selected', 'error')
                problem_info['testcases'] = Problem.find_one({'id': id}).testcases
            else:
                testcase_file_path = os.path.join(app.config['UPLOADS_PATH'], f'{id}.zip')
                testcase_file.save(testcase_file_path)
                dir = os.path.join(app.config['UPLOADS_PATH'], id)

                try:
                    # any errors happen after this point (should be) related to the testcase file format
                    with zipfile.ZipFile(testcase_file_path, 'r') as zip_ref:
                        zip_ref.extractall(dir)
                    if sum([1 for file in os.listdir(dir) if os.path.isfile(os.path.join(dir, file))]) == 0:
                        # copy files in the inside directory
                        inside_dir = os.path.join(dir, os.listdir(dir)[0])
                        for file in os.listdir(inside_dir):
                            os.rename(os.path.join(inside_dir, file), os.path.join(dir, file))
                        os.rmdir(inside_dir)
                    inputs = {}
                    outputs = {}
                    testcase_numbers = set()
                    for file in os.listdir(dir):
                        if not file.endswith('.in') and not file.endswith('.out'):
                            continue
                        batch_number, testcase_number, file_type = file.split('.')
                        batch_number = int(batch_number)
                        testcase_number = int(testcase_number)
                        testcase_numbers.add((batch_number, testcase_number))
                        if file_type == 'in':
                            inputs[(batch_number, testcase_number)] = open(os.path.join(dir, file), 'r').read()
                        elif file_type == 'out':
                            outputs[(batch_number, testcase_number)] = open(os.path.join(dir, file), 'r').read()
                    
                    for tn in sorted(list(testcase_numbers)):
                        testcases.append(Testcase(inputs[tn], outputs[tn], tn[0]))

                except Exception as e:
                    logging.error(e)
                    flash('Invalid testcase file', 'error')
                
                problem_info['testcases'] = testcases
                shutil.rmtree(dir, ignore_errors=False, onerror=None)

        judge_method = request.form.get('judge-method')
        if judge_method == 'grader':
            grader_code = request.form['grader-code']
            grader_language = Language.cast_from_document(request.form['grader-language'])
            problem_info['grader_source_code'] = SourceCode(grader_code, grader_language)
        
        if 'restrict-langs' in request.form:
            allowed_languages = [Language.cast_from_document(lang) for lang in request.form.getlist('allowed-languages')]
        else:
            allowed_languages = None
        problem_info['allowed_languages'] = allowed_languages
            
        problem = Problem(**problem_info)
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

@admin_bp.route('/create/assignment', methods=['POST'])
def create_assignment():
    assignment = Assignment(current_user.username)
    assignment.save(wait=True)
    flash('Assignment created', 'success')
    return redirect(url_for('admin_bp.edit_assignment', id=assignment.id))

@admin_bp.route('/edit/assignment/<int:id>', methods=['GET', 'POST'])
def edit_assignment(id: int):
    assignment = Assignment.find_one({'id': id})
    if request.method == 'POST':
        # JS guarantees there is at least one user group and one problem selected.
        user_group_ids = [
            int(u_g_id)
            for u_g_id in request.form.get('selected_user_group_ids').split(',')
        ]
        problem_ids = request.form.get('selected_problem_ids').split(',')

        assignment.problem_ids = problem_ids
        assignment.user_group_ids = user_group_ids
        assignment.visible = 'visible-checkbox' in request.form
        assignment.save(wait=True, replace=True)

        flash('Assignment created', 'success')
        return redirect(url_for('admin_bp.assignments'))
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

@admin_bp.route('/guide')
def admin_guide():
    return render_template('admin_guide.html')