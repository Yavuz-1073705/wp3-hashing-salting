from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for LearningGoal and Keyword
learning_goal_keywords = db.Table('learning_goal_keywords',
    db.Column('learning_goal_id', db.String(64), db.ForeignKey('learning_goal.id'), primary_key=True),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    snapshots = db.relationship('Snapshot', backref='student', lazy='dynamic')

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

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
    password_hash = db.Column(db.String(256), nullable=False)
    # role: 'student' or 'teacher'
    role = db.Column(db.String(20), nullable=False, default='student')
    # Foreign key to the Student record (only used for role 'student')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    student = db.relationship('Student', backref=db.backref('user', uselist=False))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'role': self.role}
