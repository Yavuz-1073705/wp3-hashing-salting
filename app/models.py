from datetime import datetime, timezone

from app import db
from app.services.passwords import hash_password, needs_rehash, verify_password

# Association table for LearningGoal and Keyword
learning_goal_keywords = db.Table('learning_goal_keywords',
    db.Column('learning_goal_id', db.String(64), db.ForeignKey('learning_goal.id'), primary_key=True),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True)
)


class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    students = db.relationship('Student', backref='school_class', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'student_count': self.students.count(),
        }

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)
    snapshots = db.relationship('Snapshot', backref='student', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'class_id': self.class_id,
            'class_name': self.school_class.name if self.school_class else None,
        }

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    learning_goals = db.relationship('LearningGoal', backref='subject', lazy='dynamic')

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return f'<Keyword {self.word}>'

class LearningGoal(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(256))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    keywords = db.relationship('Keyword', secondary=learning_goal_keywords, backref='learning_goals')
    snapshots = db.relationship('Snapshot', backref='learning_goal', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'keywords': [k.word for k in self.keywords]
        }

class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    learning_goal_id = db.Column(db.String(64), db.ForeignKey('learning_goal.id'))
    date = db.Column(db.String(10))  # Storing as string YYYY-MM-DD for simplicity
    source_type = db.Column(db.String(32))
    source_id = db.Column(db.String(32))
    taxonomy_scores = db.relationship('TaxonomyScore', backref='snapshot', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'source': {'type': self.source_type, 'id': self.source_id},
            'learning_goal_id': self.learning_goal_id,
            'taxonomy': [t.to_dict() for t in self.taxonomy_scores]
        }

class TaxonomyScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    snapshot_id = db.Column(db.Integer, db.ForeignKey('snapshot.id'))
    level = db.Column(db.String(32))
    kennen = db.Column(db.Float)
    kunnen = db.Column(db.Float)
    confidence = db.Column(db.Float)

    def to_dict(self):
        return {
            'level': self.level,
            'kennen': self.kennen,
            'kunnen': self.kunnen,
            'confidence': self.confidence
        }


class User(db.Model):
    """Application user: either a student or a teacher."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Argon2id hash string: contains algorithm, parameters, salt and hash.
    password_hash = db.Column(db.String(256), nullable=False)
    # When the current hash was created. NULL = old Werkzeug hash from before
    # the switch to Argon2id that has not been upgraded yet.
    password_updated_at = db.Column(db.DateTime, nullable=True)
    # role: 'student' or 'teacher'
    role = db.Column(db.String(20), nullable=False, default='student')
    # Foreign key to the Student record (only used for role 'student')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    student = db.relationship('Student', backref=db.backref('user', uselist=False))

    def set_password(self, password):
        """Store an Argon2id hash (with a new random salt) of the password."""
        self.password_hash = hash_password(password)
        self.password_updated_at = datetime.now(timezone.utc)

    def check_password(self, password):
        """Verify the password and upgrade an outdated hash to Argon2id.

        Returns True when the password is correct. The caller must commit the
        session so an upgraded hash is saved.
        """
        if not verify_password(self.password_hash, password):
            return False
        if needs_rehash(self.password_hash):
            self.set_password(password)
        return True

    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'role': self.role}
