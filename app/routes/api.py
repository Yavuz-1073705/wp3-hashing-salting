from collections import defaultdict

from flask import Blueprint, jsonify, request, g
from app import db
from app.models import Student, Subject, LearningGoal, Snapshot, TaxonomyScore, SchoolClass

bp = Blueprint('api', __name__)


def _require_login():
    """Return a 401 JSON response if the user is not logged in, else None."""
    if not g.current_user:
        return jsonify({'error': 'Niet ingelogd'}), 401
    return None


def _require_teacher():
    """Return a 403 JSON response if the user is not a teacher, else None."""
    err = _require_login()
    if err:
        return err
    if g.current_user.role != 'teacher':
        return jsonify({'error': 'Toegang geweigerd'}), 403
    return None


@bp.route('/students')
def get_students():
    """Return a list of all students. Teacher only."""
    err = _require_teacher()
    if err:
        return err
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])


@bp.route('/students/<int:student_id>')
def get_student(student_id):
    """Return a single student with their learning goals and snapshots."""
    err = _require_login()
    if err:
        return err

    # Students may only access their own data
    if g.current_user.role == 'student' and g.current_user.student_id != student_id:
        return jsonify({'error': 'Toegang geweigerd'}), 403

    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student niet gevonden'}), 404

    filter_subject = request.args.get('subject')
    filter_learning_goal = request.args.get('learning_goal')
    filter_keyword = request.args.get('keyword')
    filter_date_from = request.args.get('date_from')
    filter_date_to = request.args.get('date_to')

    snapshots = Snapshot.query.filter_by(student_id=student.id).all()

    if not snapshots:
        return jsonify({'student': student.to_dict(), 'learningGoals': []})

    # Bulk-load taxonomy scores and learning goals to avoid N+1 queries
    snap_ids = [s.id for s in snapshots]
    lg_ids = list(set(s.learning_goal_id for s in snapshots))

    all_tax = TaxonomyScore.query.filter(TaxonomyScore.snapshot_id.in_(snap_ids)).all()
    scores_by_snap = defaultdict(list)
    for ts in all_tax:
        scores_by_snap[ts.snapshot_id].append(ts.to_dict())

    all_lgs = LearningGoal.query.filter(LearningGoal.id.in_(lg_ids)).all()
    lg_dict = {lg.id: lg for lg in all_lgs}

    # Group snapshots by learning goal
    goals_map = {}
    for snap in snapshots:
        if filter_date_from and snap.date < filter_date_from:
            continue
        if filter_date_to and snap.date > filter_date_to:
            continue

        lg_id = snap.learning_goal_id
        if lg_id not in goals_map:
            lg = lg_dict.get(lg_id)
            if not lg:
                continue

            if filter_subject:
                if not lg.subject or lg.subject.name != filter_subject:
                    continue

            if filter_learning_goal and lg.title != filter_learning_goal:
                continue

            if filter_keyword:
                if filter_keyword not in [k.word for k in lg.keywords]:
                    continue

            goals_map[lg_id] = {
                'id': lg.id,
                'title': lg.title,
                'subject': lg.subject.to_dict() if lg.subject else None,
                'keywords': [k.word for k in lg.keywords],
                'snapshots': []
            }

        if lg_id in goals_map:
            goals_map[lg_id]['snapshots'].append({
                'id': snap.id,
                'date': snap.date,
                'source': {'type': snap.source_type, 'id': snap.source_id},
                'learning_goal_id': snap.learning_goal_id,
                'taxonomy': scores_by_snap.get(snap.id, [])
            })

    return jsonify({
        'student': student.to_dict(),
        'learningGoals': list(goals_map.values())
    })


@bp.route('/subjects')
def get_subjects():
    """Return a list of all subjects. Requires login."""
    err = _require_login()
    if err:
        return err
    subjects = Subject.query.all()
    return jsonify([s.to_dict() for s in subjects])


@bp.route('/class-overview')
def get_class_overview():
    """Return aggregated class-level overview for the teacher dashboard. Teacher only."""
    err = _require_teacher()
    if err:
        return err

    class_id = request.args.get('class_id', type=int)
    from app.services.analysis import get_class_overview
    return jsonify(get_class_overview(class_id=class_id))


@bp.route('/classes')
def get_classes():
    """Return all classes with student counts. Teacher only."""
    err = _require_teacher()
    if err:
        return err

    classes = SchoolClass.query.order_by(SchoolClass.name).all()
    return jsonify([c.to_dict() for c in classes])


@bp.route('/classes', methods=['POST'])
def create_class():
    """Create a new class. Teacher only."""
    err = _require_teacher()
    if err:
        return err

    payload = request.get_json(silent=True) or {}
    name = (payload.get('name') or '').strip()

    if not name:
        return jsonify({'error': 'Klasnaam is verplicht'}), 400

    existing = SchoolClass.query.filter(db.func.lower(SchoolClass.name) == name.lower()).first()
    if existing:
        return jsonify({'error': 'Deze klas bestaat al'}), 409

    school_class = SchoolClass(name=name)
    db.session.add(school_class)
    db.session.commit()
    return jsonify(school_class.to_dict()), 201


@bp.route('/students/<int:student_id>/class', methods=['POST'])
def assign_student_class(student_id):
    """Assign or clear class for one student. Teacher only."""
    err = _require_teacher()
    if err:
        return err

    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student niet gevonden'}), 404

    payload = request.get_json(silent=True) or {}
    class_id = payload.get('class_id')

    if class_id in (None, '', 0):
        student.class_id = None
        db.session.commit()
        return jsonify(student.to_dict())

    try:
        class_id = int(class_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Ongeldige klas'}), 400

    school_class = db.session.get(SchoolClass, class_id)
    if not school_class:
        return jsonify({'error': 'Klas niet gevonden'}), 404

    student.class_id = school_class.id
    db.session.commit()
    return jsonify(student.to_dict())
