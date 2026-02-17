from flask import Blueprint, render_template, abort
from app import db
from app.models import Student

bp = Blueprint('student', __name__)


@bp.route('/')
def landing():
    """Student landing page - shows list of all students."""
    students = Student.query.order_by(Student.name).all()
    return render_template('student/landing.html', students=students)


@bp.route('/dashboard/<int:student_id>')
def dashboard(student_id):
    """Student dashboard shell. All data is loaded via AJAX from the API."""
    student = db.session.get(Student, student_id)
    if not student:
        abort(404)

    return render_template('student/dashboard.html', student=student)
