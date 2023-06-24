from flask import Blueprint, jsonify, send_from_directory, current_app as app
import os
from flask_login import current_user

uploads_bp = Blueprint('uploads_bp', __name__)


@uploads_bp.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@uploads_bp.route('/<problem_id>', methods=['GET', 'POST'])
def download(problem_id):
    if not current_user.is_contributor():
        return 'Forbidden', 403
    path = problem_id + '.zip'
    if not os.path.exists(os.path.join(app.config['UPLOADS_PATH'], path)):
        return 'File not found', 404
    return send_from_directory(directory=app.config['UPLOADS_PATH'], path=path)

