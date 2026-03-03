import os
import click
from flask import Flask, g, session
from config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    @app.cli.command('import-data')
    @click.argument('filepath', default=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'data-sample-small.json'))
    def import_data_command(filepath):
        """Import JSON data into the database."""
        from app.services.importer import import_data
        print(f"Importing from {filepath}...")
        import_data(filepath)

    return app
