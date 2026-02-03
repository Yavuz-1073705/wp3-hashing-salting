from flask import Blueprint, jsonify

bp = Blueprint('api', __name__)

@bp.route('/stats')
def stats():
    return jsonify({"status": "ok"})
