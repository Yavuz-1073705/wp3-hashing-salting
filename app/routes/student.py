from flask import Blueprint, render_template

bp = Blueprint('student', __name__)


@bp.route('/')
def landing():
    """Student landing page - login not yet implemented."""
    return render_template('student/landing.html')
