from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from flask_login import current_user

from website.celery_tasks import judge
from website.models import Problem, Submission, Assignment
from isolate_wrapper import Language


problem_bp = Blueprint(
    'problem_bp', __name__, template_folder='templates', static_folder='static'
)


@problem_bp.route('/<id>')
def problem(id: str) -> str:
    problem = Problem.find_one({'id': id})
    if problem is None:
        abort(404, description="Problem not found")
    user_assignments = Assignment.find_all({'user_group_ids': {'$in': current_user.user_group_ids}})
    can_view = any(problem.id in assignment.problem_ids for assignment in user_assignments)
    if not current_user.is_contributor() and not problem.is_public and not can_view:
        abort(403, 'Problem is not public')
    example_testcases = [testcase for testcase in problem.get_testcases() if testcase.batch_number == 0]
    allowed_languages=problem.allowed_languages if problem.allowed_languages is not None else list(Language)
    return render_template('problem.html', problem=problem, example_testcases=example_testcases, allowed_languages=allowed_languages)


# @problem_bp.route('/<id>/submit', methods=['POST'])
# def problem_submit(id: str):
#     user_id = current_user.id
#     user_code = request.form.get('user_code')
#     language = Language.cast_from_document(request.form.get('language'))
#     new_submission = Submission(user_id=user_id, problem_id=id, code=user_code, language=language)
#     problem = Problem.find_one({'id': id})
#     new_submission.create_empty_results(len(problem.testcases))
#     submission_id = new_submission.save(wait=True).id
#     grader_source_code_dict = problem.grader_source_code.cast_to_document() if problem.grader_source_code is not None else None
#     judge.delay(
#         user_code, language.cast_to_document(), new_submission.cast_to_document(), id, grader_source_code_dict
#     )
#     return redirect(url_for('submission_bp.submission', id=submission_id))
