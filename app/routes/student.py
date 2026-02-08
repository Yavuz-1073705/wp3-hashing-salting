from flask import Blueprint, render_template, abort
from app import db
from app.models import Student, Snapshot, LearningGoal

bp = Blueprint('student', __name__)


@bp.route('/')
def select():
    """Page to select a student."""
    students = Student.query.order_by(Student.name).all()
    return render_template('student/select.html', students=students)


@bp.route('/<int:student_id>')
def dashboard(student_id):
    """Student dashboard with learning goals and snapshots."""
    student = db.session.get(Student, student_id)
    if not student:
        abort(404)

    snapshots = Snapshot.query.filter_by(student_id=student.id).all()

    # Group by learning goal
    goals = {}
    for snap in snapshots:
        lg_id = snap.learning_goal_id
        if lg_id not in goals:
            lg = db.session.get(LearningGoal, lg_id)
            goals[lg_id] = {
                'id': lg.id,
                'title': lg.title,
                'subject': lg.subject.name if lg.subject else '',
                'keywords': [k.word for k in lg.keywords],
                'snapshots': []
            }
        goals[lg_id]['snapshots'].append({
            'date': snap.date,
            'source_type': snap.source_type,
            'source_id': snap.source_id,
            'taxonomy': [t.to_dict() for t in snap.taxonomy_scores]
        })

    # Sort snapshots by date within each goal
    for goal in goals.values():
        goal['snapshots'].sort(key=lambda s: s['date'])

    return render_template('student/dashboard.html', student=student, goals=list(goals.values()))
