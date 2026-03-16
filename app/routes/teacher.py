from flask import Blueprint, render_template, abort, redirect, url_for, g, flash, request
from app import db
from app.models import Student, Snapshot, LearningGoal, User

bp = Blueprint('teacher', __name__)


def _require_teacher():
    """Redirect unauthenticated or non-teacher users."""
    if not g.current_user:
        flash('Je moet ingelogd zijn om deze pagina te bezoeken.', 'warning')
        return redirect(url_for('auth.login'))
    if g.current_user.role != 'teacher':
        flash('Alleen docenten hebben toegang tot dit gedeelte.', 'error')
        return redirect(url_for('main.index'))
    return None


@bp.route('/')
def dashboard():
    """Teacher dashboard: list of all students."""
    redirect_response = _require_teacher()
    if redirect_response:
        return redirect_response

    students = Student.query.order_by(Student.name).all()
    # IDs of students that already have a linked user account
    students_with_account = {
        u.student_id
        for u in User.query.filter(User.student_id.isnot(None)).all()
    }
    return render_template(
        'teacher/dashboard.html',
        students=students,
        students_with_account=students_with_account,
    )


@bp.route('/student/<int:student_id>')
def student_detail(student_id):
    """Teacher view: student detail with learning goals and snapshots."""
    redirect_response = _require_teacher()
    if redirect_response:
        return redirect_response

    student = db.session.get(Student, student_id)
    if not student:
        abort(404)

    student_user = User.query.filter_by(student_id=student.id).first()
    suggested_email = student.name.lower().replace(' ', '.') + '@leerling.nl'

    snapshots = Snapshot.query.filter_by(student_id=student.id).all()

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

    for goal in goals.values():
        goal['snapshots'].sort(key=lambda s: s['date'])

    return render_template(
        'teacher/student_detail.html',
        student=student,
        goals=list(goals.values()),
        student_user=student_user,
        suggested_email=suggested_email,
    )


@bp.route('/student/<int:student_id>/create-account', methods=['POST'])
def create_student_account(student_id):
    """Create a login account for a student (teacher only)."""
    redirect_response = _require_teacher()
    if redirect_response:
        return redirect_response

    student = db.session.get(Student, student_id)
    if not student:
        abort(404)

    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not email or not password:
        flash('E-mailadres en wachtwoord zijn verplicht.', 'error')
        return redirect(url_for('teacher.student_detail', student_id=student_id))

    if len(password) < 6:
        flash('Wachtwoord moet minimaal 6 tekens zijn.', 'error')
        return redirect(url_for('teacher.student_detail', student_id=student_id))

    if User.query.filter_by(email=email).first():
        flash('Dit e-mailadres is al in gebruik. Kies een ander adres.', 'error')
        return redirect(url_for('teacher.student_detail', student_id=student_id))

    user = User(email=email, role='student', student_id=student.id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash(f'Account aangemaakt voor {student.name} ({email}).', 'info')
    return redirect(url_for('teacher.student_detail', student_id=student_id))
