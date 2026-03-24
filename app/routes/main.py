from flask import Blueprint, redirect, url_for, g

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    user = g.get('current_user')
    if not user:
        return redirect(url_for('auth.login'))
    if user.role == 'teacher':
        return redirect(url_for('teacher.dashboard'))
    if user.role == 'student' and user.student_id:
        return redirect(url_for('student.dashboard', student_id=user.student_id))
    return redirect(url_for('auth.login'))
