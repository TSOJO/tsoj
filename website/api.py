from flask import Blueprint, jsonify, abort, request
import json
import time
from flask_login import current_user

from website.models import Problem, Submission, User, Assignment, DBModel
from isolate_wrapper import IsolateSandbox, Verdict, SourceCode, Language
from website.utils import to_input_format
from website.celery_tasks import judge

api_bp = Blueprint('api_bp', __name__)


@api_bp.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@api_bp.route('/get-problem-max-ids', methods=['GET'])
def get_problem_max_ids():
    problem_max_ids = {}
    for problem in Problem.find_all():
        try:
            head, number = problem.id.split('-')
            number = int(number)
        except ValueError:
            abort(400, description="Problems database contained an invalid problem ID.")
        if head not in problem_max_ids:
            problem_max_ids[head] = number
        else:
            problem_max_ids[head] = max(problem_max_ids[head], number)
    return problem_max_ids        


@api_bp.route('/get-outputs', methods=['POST'])
def get_outputs():
    # {
    #     problem_id: str
    #     code: str
    #     language: str
    #     inputs: List[str]
    #     time_limit: str, in seconds
    #     memory_limit: str, in MB
    # }
    # returns
    # List[{
    #     'output': output,
    #     'verdict': verdict.cast_to_document(),
    #     'message': message,
    # }]
    req_json = json.loads(request.data)

    problem_id = req_json.get('problem_id')
    code = req_json.get('code')
    language = Language.cast_from_document(req_json.get('language'))
    inputs = req_json.get('inputs')
    time_limit = req_json.get('time_limit')
    memory_limit = req_json.get('memory_limit')

    if any(param is None for param in (code, language, inputs, time_limit, memory_limit)):
        abort(400, description='Invalid parameters')

    try:
        time_limit = int(float(time_limit) * 1000)
        memory_limit = int(float(memory_limit) * 1024)
    except ValueError:
        abort(400, description='Invalid parameters')

    source_code = SourceCode(code, language)
    if problem_id is not None:
        problem = Problem.find_one({'id': problem_id})
        source_code.aqaasm_inputs = problem.aqaasm_inputs
        source_code.aqaasm_outputs = problem.aqaasm_outputs

    results = []
    sandbox = IsolateSandbox()
    for (output, result) in sandbox.get_outputs(
        source_code, inputs, time_limit, memory_limit
    ):
        results.append(
            {
                'output': output,
                'verdict': result.verdict.cast_to_document(),
                'time': result.time,
                'memory': result.memory,
                'message': result.message,
            }
        )
        if result.verdict != Verdict.AC:
            break
    return jsonify(results)

@api_bp.route('/test-grader', methods=['POST'])
def test_grader():
    req_json = json.loads(request.data)
    grader_code = req_json.get('grader_code')
    language = Language.cast_from_document(req_json.get('language'))
    inputs = req_json.get('inputs')
    outputs = req_json.get('outputs')
    time_limit = req_json.get('time_limit')
    memory_limit = req_json.get('memory_limit')

    if any(param is None for param in (grader_code, language, inputs, outputs, time_limit, memory_limit)):
        abort(400, description='Invalid parameters')
    
    try:
        time_limit = int(float(time_limit) * 1000)
        memory_limit = int(float(memory_limit) * 1024)
    except ValueError:
        abort(400, description='Invalid parameters')

    new_inputs = [to_input_format(input) + '\n' + output for (input, output) in zip(inputs, outputs)]
    
    sandbox = IsolateSandbox()
    for (index, (grader_output, verdict, message)) in enumerate(sandbox.get_outputs(
        SourceCode(grader_code, language), new_inputs, time_limit, memory_limit
    )):
        if verdict != Verdict.AC:
            return jsonify(
                {
                    'index': index + 1,
                    'output': grader_output,
                    'verdict': verdict.cast_to_document(),
                    'message': message,
                }
            )
        elif grader_output.strip() != 'AC':
            return jsonify(
                {
                    'index': index + 1,
                    'output': grader_output,
                    'verdict': Verdict.SE.cast_to_document(),
                    'message': 'Grader outputted non-AC',
                }
            )
    return jsonify(
        {
            'output': '',
            'verdict': Verdict.AC.cast_to_document(),
            'message': '',
        }
    )


@api_bp.route('/capture-submission-change/', methods=['POST'])
def capture_submission_change():
    # Long poll for submission change.
    req_json = json.loads(request.data)
    submission_id = req_json.get('id')
    tests_completed = req_json.get('tests_completed')

    try:
        submission_id = int(submission_id)
        tests_completed = int(tests_completed)
    except (ValueError, TypeError):
        abort(400, description='Invalid parameters')

    # This will hold the request for {hold_for} seconds, and will return whenever submission changes.
    submission = Submission.find_one({'id': submission_id})
    if submission is None:
        abort(404, description='Submission not found')

    def submission_as_json():
        return jsonify(
            {
                'final_verdict': submission.final_verdict.cast_to_document(),
                'tests_completed': submission.tests_completed(),
                'results': [r.cast_to_document() for r in submission.results],
            }
        )

    if submission.final_verdict is not Verdict.WJ:
        # Already done
        return submission_as_json()

    poll_rate = 0.5  # s
    hold_for = 5  # s
    for _ in range(int(hold_for // poll_rate)):
        time.sleep(poll_rate)
        if submission.tests_completed() != tests_completed:
            return submission_as_json()
        submission = Submission.find_one({'id': submission_id})

    # Return it anyway...
    return submission_as_json()

@api_bp.route('/problem-submit/<id>', methods=['POST'])
def problem_submit(id: str):
    user_id = current_user.id
    user_code = request.form.get('user_code')
    language = Language.cast_from_document(request.form.get('language'))
    new_submission = Submission(user_id=user_id, problem_id=id, code=user_code, language=language)
    problem = Problem.find_one({'id': id})
    submission_id = new_submission.save(wait=True).id
    grader_source_code_dict = problem.grader_source_code.cast_to_document() if problem.grader_source_code is not None else None
    judge.delay(
        user_code, language.cast_to_document(), new_submission.cast_to_document(), id, grader_source_code_dict
    )
    return jsonify({'submission_id': submission_id})