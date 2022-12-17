from flask import Blueprint, jsonify, abort, request
from website.models import Problem
from isolate_wrapper import IsolateSandbox
import json

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
    print(req_json)
    code = req_json.get('generatorCode')
    input_ = req_json.get('input')
    time_limit = req_json.get('timeLimit')
    memory_limit = req_json.get('memoryLimit')

    print(code, input_, time_limit, memory_limit)

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
        'verdict': verdict.name,
    })
