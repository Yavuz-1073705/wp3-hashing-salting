import json
from app import db
from app.models import Student, Subject, LearningGoal, Keyword, Snapshot, TaxonomyScore


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    instance = model(**kwargs)
    session.add(instance)
    session.commit()
    return instance


def import_entry(entry):
    """Import a single student-subject entry into the database."""
    # Student
    student_data = entry.get('student', {})
    student = get_or_create(db.session, Student, id=student_data['id'], name=student_data['name'])

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


def import_data(filepath):
    """Import JSON data file. Supports both single entry and entries[] format."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        entries = data.get('entries', [data])
        count = 0

        for entry in entries:
            student, subject = import_entry(entry)
            count += 1
            print(f"  [{count}/{len(entries)}] {student.name} - {subject.name}")

        print(f"Successfully imported {count} entries.")
        return True

    except Exception as e:
        print(f"Error importing data: {e}")
        db.session.rollback()
        return False
