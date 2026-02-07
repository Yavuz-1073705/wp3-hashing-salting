from flask import Blueprint, render_template

bp = Blueprint('teacher', __name__)

@bp.route('/')
def dashboard():
    return render_template('teacher/dashboard.html')
