from flask import Blueprint, render_template, abort, redirect, url_for, g, flash
from app import db
from app.models import Student, User

bp = Blueprint('student', __name__)


def _require_login():
    """Redirect unauthenticated users to the login page."""
    if not g.current_user:
        flash('Je moet ingelogd zijn om deze pagina te bezoeken.', 'warning')
        return redirect(url_for('auth.login'))
    return None


@bp.route('/')
def landing():
    """Student landing page - only accessible when logged in."""
    redirect_response = _require_login()
    if redirect_response:
        return redirect_response

    user = g.current_user
    # Students are redirected directly to their own dashboard
    if user.role == 'student':
        if user.student_id:
            return redirect(url_for('student.dashboard', student_id=user.student_id))
        # Account exists but has no linked student record yet
        return render_template('student/landing.html', students=[])

    # Teachers are allowed to see the full student list
    if user.role == 'teacher':
        students = Student.query.order_by(Student.name).all()
        return render_template('student/landing.html', students=students)

    return redirect(url_for('main.index'))


@bp.route('/dashboard/<int:student_id>')
def dashboard(student_id):
    """Student dashboard shell. All data is loaded via AJAX from the API."""
    redirect_response = _require_login()
    if redirect_response:
        return redirect_response

    user = g.current_user
    # Students may only view their own dashboard
    if user.role == 'student' and user.student_id != student_id:
        flash('Je hebt geen toegang tot het dashboard van een andere leerling.', 'error')
        return redirect(url_for('student.dashboard', student_id=user.student_id))

    student = db.session.get(Student, student_id)
    if not student:
        abort(404)

    student_user = User.query.filter_by(student_id=student.id).first()
    return render_template('student/dashboard.html', student=student, student_user=student_user)
