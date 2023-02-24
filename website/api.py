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


@api_bp.route('/generate-answer', methods=['POST'])
def generate_answer():
    req_json = json.loads(request.data)
    code = req_json.get('generator_code')
    language = Language.cast_from_document(req_json.get('language'))
    input_ = req_json.get('input')
    time_limit = req_json.get('time_limit')
    memory_limit = req_json.get('memory_limit')

    if any(param is None for param in (code, language, input_, time_limit, memory_limit)):
        abort(400, description='Invalid parameters')

    try:
        time_limit = int(float(time_limit) * 1000)
        memory_limit = int(float(memory_limit) * 1024)
    except ValueError:
        abort(400, description='Invalid parameters')

    answer, verdict, message = IsolateSandbox().get_output(
        SourceCode(code, language), input_, time_limit, memory_limit
    )
    return jsonify(
        {
            'answer': answer,
            'verdict': verdict.cast_to_document(),
            'message': message,
        }
    )

@api_bp.route('/test-grader', methods=['POST'])
def test_grader():
    req_json = json.loads(request.data)
    grader_code = req_json.get('grader_code')
    language = Language.cast_from_document(req_json.get('language'))
    input_ = req_json.get('input')
    output = req_json.get('output')
    time_limit = req_json.get('time_limit')
    memory_limit = req_json.get('memory_limit')

    if any(param is None for param in (grader_code, language, input_, output, time_limit, memory_limit)):
        abort(400, description='Invalid parameters')
    
    try:
        time_limit = int(float(time_limit) * 1000)
        memory_limit = int(float(memory_limit) * 1024)
    except ValueError:
        abort(400, description='Invalid parameters')

    new_input = to_input_format(input_) + '\n' + output
    print(new_input)
    grader_output, verdict, message = IsolateSandbox().get_output(
        SourceCode(grader_code, language), new_input, time_limit, memory_limit
    )
    return jsonify(
        {
            'output': grader_output,
            'verdict': verdict.cast_to_document(),
            'message': message,
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
