from flask import Blueprint, render_template

bp = Blueprint('student', __name__)

@bp.route('/<int:student_id>')
def dashboard(student_id):
    return render_template('student/dashboard.html')
