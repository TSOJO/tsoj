from flask import Blueprint, jsonify, abort, request
from website.models import Problem, Submission
from isolate_wrapper import IsolateSandbox
import json
import time

api_bp = Blueprint('api_bp', __name__)

@api_bp.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@api_bp.route('/problem/<id>')
def fetch_problem(id):
    problem_obj = Problem.find_one({'id': id})
    if problem_obj is None:
        abort(404, description="Problem not found")
    return jsonify(problem_obj.cast_to_document())

@api_bp.route('/generate-answer', methods=['POST'])
def generate_answer():
    req_json = json.loads(request.data)
    code = req_json.get('generatorCode')
    input_ = req_json.get('input')
    time_limit = req_json.get('timeLimit')
    memory_limit = req_json.get('memoryLimit')

    if any(param is None for param in (code, input_, time_limit, memory_limit)):
        abort(400, description="Invalid parameters")

    try:
        time_limit = int(float(time_limit) * 1000)
        memory_limit = int(float(memory_limit) * 1024)
    except ValueError:
        abort(400, description="Invalid parameters")
    
    answer, verdict = IsolateSandbox().generate_answer(code, input_, time_limit, memory_limit)
    return jsonify({
        'answer': answer,
        'verdict': verdict.cast_to_document(),
    })

@api_bp.route('/grab-submission-change/', methods=['POST'])
def grab_submission_change():
    req_json = json.loads(request.data)
    submission_id = req_json.get('id')
    tests_completed = req_json.get('testsCompleted')
    
    # redundant, int(None) will raise TypeError
    # if any(param is None for param in (submission_id, tests_completed)):
    #     abort(400, description="Invalid parameters")
    
    try:
        submission_id = int(submission_id)
        tests_completed = int(tests_completed)
    except (ValueError, TypeError):
        abort(400, description="Invalid parameters")  
        
    # This will hold the request for {hold_for} seconds, and will return whenever submission changes.
    submission_now = Submission.find_one({'id': submission_id})

    if tests_completed == len(submission_now.results):
        # Already done
        return jsonify({
                'finalVerdict': submission_now.final_verdict.cast_to_document(),
                'testsCompleted': tests_completed,
                'results': [r.cast_to_document() for r in submission_now.results]
            })
        
    if submission_now is None:
        abort(404, description='Submission not found')

    poll_rate = 0.5  # s
    hold_for = 5  # s
    for _ in range(int(hold_for // poll_rate)):
        time.sleep(poll_rate)
        now_completed = submission_now.tests_completed()
        if now_completed != tests_completed:
            return jsonify({
                'finalVerdict': submission_now.final_verdict.cast_to_document(),
                'testsCompleted': now_completed,
                'results': [r.cast_to_document() for r in submission_now.results]
            })
        submission_now = Submission.find_one({'id': submission_id})
        
    # Return it anyway...
    return jsonify({
                'finalVerdict': submission_now.final_verdict.cast_to_document(),
                'testsCompleted': now_completed,
                'results': [r.cast_to_document() for r in submission_now.results]
            })