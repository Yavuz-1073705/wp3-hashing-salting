import os
import click
from flask import Flask, g, session, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def _ensure_schema_compatibility():
    """Apply small additive schema updates for local SQLite databases."""
    result = db.session.execute(text("PRAGMA table_info(student)"))
    existing_columns = {row[1] for row in result.fetchall()}
    if 'class_id' not in existing_columns:
        db.session.execute(text("ALTER TABLE student ADD COLUMN class_id INTEGER"))
        db.session.commit()

    result = db.session.execute(text("PRAGMA table_info(user)"))
    user_columns = {row[1] for row in result.fetchall()}
    if 'password_updated_at' not in user_columns:
        # Existing rows keep NULL: their old Werkzeug hash is upgraded to
        # Argon2id on the next successful login.
        db.session.execute(text("ALTER TABLE user ADD COLUMN password_updated_at DATETIME"))
        db.session.commit()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.routes.main import bp as main_bp
    from app.routes.student import bp as student_bp
    from app.routes.teacher import bp as teacher_bp
    from app.routes.api import bp as api_bp
    from app.routes.auth import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    with app.app_context():
        db.create_all()
        _ensure_schema_compatibility()

    @app.before_request
    def load_logged_in_user():
        """Load the logged-in user into g.current_user before every request."""
        from app.models import User
        g.current_user = None
        user_id = session.get('user_id')
        if user_id:
            g.current_user = db.session.get(User, user_id)

    @app.context_processor
    def inject_user():
        """Make current_user available in all Jinja templates."""
        return {'current_user': g.get('current_user')}

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.cli.command('import-data')
    @click.argument('filepath', default=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'data-sample-small.json'))
    def import_data_command(filepath):
        """Import JSON data and ensure a default teacher account exists."""
        from app.services.importer import import_data
        from app.models import User
        print(f"Importing from {filepath}...")
        import_data(filepath, default_class_name='Onbekende klas')

        if not User.query.filter_by(email='docent@school.nl').first():
            teacher = User(email='docent@school.nl', role='teacher')
            teacher.set_password('docent123')
            db.session.add(teacher)
            db.session.commit()
            print('Docent aangemaakt: docent@school.nl / docent123')

    @app.cli.command('seed-users')
    def seed_users_command():
        """Create default test users (one teacher + one student account per student record)."""
        from app.models import User, Student
        added = 0

        # Teacher account
        if not User.query.filter_by(email='docent@school.nl').first():
            teacher = User(email='docent@school.nl', role='teacher')
            teacher.set_password('docent123')
            db.session.add(teacher)
            added += 1
            print('Docent aangemaakt: docent@school.nl / docent123')

        # Student accounts for all existing student records
        for student in Student.query.all():
            email = f'{student.name.lower().replace(" ", ".")}@leerling.nl'
            if not User.query.filter_by(email=email).first():
                user = User(email=email, role='student', student_id=student.id)
                user.set_password('leerling123')
                db.session.add(user)
                added += 1
                print(f'Leerling aangemaakt: {email} / leerling123')

        db.session.commit()
        print(f'{added} gebruiker(s) aangemaakt.')

    @app.cli.command('hash-status')
    def hash_status_command():
        """Show which hash algorithm each account uses (never prints hashes)."""
        from app.models import User
        from app.services.passwords import hash_algorithm
        users = User.query.order_by(User.id).all()
        for user in users:
            print(f'{user.email:<30} {hash_algorithm(user.password_hash)}')
        legacy = sum(1 for u in users if not u.password_hash.startswith('$argon2id$'))
        print(f'{len(users)} account(s), {legacy} nog met een oude hash '
              '(wordt bij de eerstvolgende login omgezet naar Argon2id).')

    return app
