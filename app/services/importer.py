import json
from app import db
from app.models import Student, Subject, LearningGoal, Keyword, Snapshot, TaxonomyScore, SchoolClass


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    instance = model(**kwargs)
    session.add(instance)
    session.commit()
    return instance


def _extract_class_name(entry):
    """Read class name from supported payload locations."""
    student_data = entry.get('student', {})
    class_data = entry.get('class')

    if isinstance(class_data, dict):
        return (class_data.get('name') or '').strip() or None
    if isinstance(class_data, str):
        return class_data.strip() or None

    for key in ('class', 'className', 'group'):
        value = student_data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def import_entry(entry, default_class_name='Onbekende klas'):
    """Import a single student-subject entry into the database."""
    # Student
    student_data = entry.get('student', {})
    student = db.session.get(Student, student_data['id'])
    if not student:
        student = Student(id=student_data['id'], name=student_data['name'])
        db.session.add(student)
    else:
        student.name = student_data['name']

    class_name = _extract_class_name(entry)
    if class_name:
        school_class = get_or_create(db.session, SchoolClass, name=class_name)
        student.class_id = school_class.id
    elif student.class_id is None and default_class_name:
        fallback_class = get_or_create(db.session, SchoolClass, name=default_class_name)
        student.class_id = fallback_class.id

    db.session.commit()

    # Subject
    subject_data = entry.get('subject', {})
    subject = get_or_create(db.session, Subject, id=subject_data['id'], name=subject_data['name'])

    # Learning Goals
    for lg_data in entry.get('learningGoals', []):
        lg_id = lg_data['id']
        lg_title = lg_data['title']

        learning_goal = db.session.get(LearningGoal, lg_id)
        if not learning_goal:
            learning_goal = LearningGoal(id=lg_id, title=lg_title, subject_id=subject.id)
            db.session.add(learning_goal)
        else:
            learning_goal.title = lg_title
            learning_goal.subject_id = subject.id
        db.session.commit()

        # Keywords
        keywords = []
        for word in lg_data.get('keywords', []):
            keywords.append(get_or_create(db.session, Keyword, word=word))
        learning_goal.keywords = keywords
        db.session.commit()

        # Snapshots
        for snap_data in lg_data.get('snapshots', []):
            source = snap_data.get('source', {})

            existing = db.session.query(Snapshot).filter_by(
                student_id=student.id,
                learning_goal_id=learning_goal.id,
                source_type=source.get('type'),
                source_id=source.get('id')
            ).first()

            if existing:
                continue

            snapshot = Snapshot(
                student_id=student.id,
                learning_goal_id=learning_goal.id,
                date=snap_data.get('at'),
                source_type=source.get('type'),
                source_id=source.get('id')
            )
            db.session.add(snapshot)
            db.session.commit()

            for tax in snap_data.get('taxonomy', []):
                score = TaxonomyScore(
                    snapshot_id=snapshot.id,
                    level=tax['level'],
                    kennen=tax['kennen'],
                    kunnen=tax['kunnen'],
                    confidence=tax['confidence']
                )
                db.session.add(score)
            db.session.commit()

    return student, subject


def import_data(filepath, default_class_name='Onbekende klas'):
    """Import JSON data file. Supports both single entry and entries[] format."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        entries = data.get('entries', [data])
        count = 0

        for entry in entries:
            student, subject = import_entry(entry, default_class_name=default_class_name)
            count += 1
            print(f"  [{count}/{len(entries)}] {student.name} - {subject.name}")

        print(f"Successfully imported {count} entries.")
        return True

    except Exception as e:
        print(f"Error importing data: {e}")
        db.session.rollback()
        return False
