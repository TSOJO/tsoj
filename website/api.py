from flask import Blueprint, jsonify, abort
from website.models import Problem

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
