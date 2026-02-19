from flask import Blueprint, jsonify, request
from app import db
from app.models import Student, Subject, LearningGoal, Snapshot

bp = Blueprint('api', __name__)


@bp.route('/students')
def get_students():
    """Return a list of all students."""
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])


@bp.route('/students/<int:student_id>')
def get_student(student_id):
    """Return a single student with their learning goals and snapshots."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student niet gevonden'}), 404

    filter_subject = request.args.get('subject')
    filter_learning_goal = request.args.get('learning_goal')
    filter_date_from = request.args.get('date_from')
    filter_date_to = request.args.get('date_to')

    snapshots = Snapshot.query.filter_by(student_id=student.id).all()

    # Group snapshots by learning goal
    goals_map = {}
    for snap in snapshots:
        # Filter by date range
        if filter_date_from and snap.date < filter_date_from:
            continue
        if filter_date_to and snap.date > filter_date_to:
            continue

        lg_id = snap.learning_goal_id
        if lg_id not in goals_map:
            lg = db.session.get(LearningGoal, lg_id)

            # Filter by subject name
            if filter_subject:
                if not lg.subject or lg.subject.name != filter_subject:
                    continue

            # Filter by learning goal title
            if filter_learning_goal and lg.title != filter_learning_goal:
                continue

            goals_map[lg_id] = {
                'id': lg.id,
                'title': lg.title,
                'subject': lg.subject.to_dict() if lg.subject else None,
                'keywords': [k.word for k in lg.keywords],
                'snapshots': []
            }

        if lg_id in goals_map:
            goals_map[lg_id]['snapshots'].append(snap.to_dict())

    return jsonify({
        'student': student.to_dict(),
        'learningGoals': list(goals_map.values())
    })


@bp.route('/subjects')
def get_subjects():
    """Return a list of all subjects."""
    subjects = Subject.query.all()
    return jsonify([s.to_dict() for s in subjects])
