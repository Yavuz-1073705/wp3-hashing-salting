from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from app import db
from app.models import User
from app.services.passwords import dummy_verify

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Display and process the login form."""
    if g.current_user:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if not user:
            # Same amount of work as for a real account (no timing leak).
            dummy_verify(password)
            return render_template('auth/login.html', error='Verkeerd e-mailadres of wachtwoord')

        if not user.check_password(password):
            return render_template('auth/login.html', error='Verkeerd e-mailadres of wachtwoord')

        # check_password() may have upgraded an old hash to Argon2id.
        db.session.commit()

        session['user_id'] = user.id

        if user.role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif user.role == 'student':
            if user.student_id:
                return redirect(url_for('student.dashboard', student_id=user.student_id))
            return redirect(url_for('student.landing'))

        return redirect(url_for('main.index'))

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """Logout and redirect to home page."""
    session.clear()
    flash('Je bent uitgelogd.', 'info')
    return redirect(url_for('main.index'))
