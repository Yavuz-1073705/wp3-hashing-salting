from flask import Blueprint, render_template

bp = Blueprint('teacher', __name__)

@bp.route('/')
def dashboard():
    # Logic to fetch class data
    return render_template('teacher/dashboard.html')
