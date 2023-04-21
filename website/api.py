from flask import Blueprint, jsonify, abort, request
import json
import time

from website.models import Problem, Submission, User, Assignment, DBModel
from isolate_wrapper import IsolateSandbox, Verdict, SourceCode, Language
from website.utils import to_input_format

api_bp = Blueprint('api_bp', __name__)


@api_bp.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@api_bp.route('/db/problem/<id>', methods=['HEAD'])
def check_problem_exists(id):
    if Problem.find_one({'id': id}) is None:
        return '', 204
    return '', 200


@api_bp.route('/generate-answers', methods=['POST'])
def generate_answers():
    req_json = json.loads(request.data)
    code = req_json.get('generator_code')
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

    results = []
    sandbox = IsolateSandbox()
    for (answer, verdict, message) in sandbox.get_outputs(
        SourceCode(code, language), inputs, time_limit, memory_limit
    ):
        results.append(
            {
                'answer': answer,
                'verdict': verdict.cast_to_document(),
                'message': message,
            }
        )
        if verdict != Verdict.AC:
            break
    # ! TEMP SOL - bug is cleanup isnt called after final yield
    sandbox.cleanup()
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
            # ! TEMP SOL - bug is cleanup isnt called after final yield
            sandbox.cleanup()
            return jsonify(
                {
                    'index': index + 1,
                    'output': grader_output,
                    'verdict': verdict.cast_to_document(),
                    'message': message,
                }
            )
        elif grader_output.strip() != 'AC':
            # ! TEMP SOL - bug is cleanup isnt called after final yield
            sandbox.cleanup()
            return jsonify(
                {
                    'index': index + 1,
                    'output': grader_output,
                    'verdict': Verdict.SE.cast_to_document(),
                    'message': 'Grader outputted non-AC',
                }
            )
    # ! TEMP SOL - bug is cleanup isnt called after final yield
    sandbox.cleanup()
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
