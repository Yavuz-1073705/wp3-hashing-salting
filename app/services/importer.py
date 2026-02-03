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

def import_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 1. Student
        student_data = data.get('student', {})
        student = get_or_create(db.session, Student, id=student_data.get('id'), name=student_data.get('name'))
        
        # 2. Subject
        subject_data = data.get('subject', {})
        subject = get_or_create(db.session, Subject, id=subject_data.get('id'), name=subject_data.get('name'))
        
        # 3. Learning Goals
        for lg_data in data.get('learningGoals', []):
            lg_id = lg_data.get('id')
            lg_title = lg_data.get('title')
            
            # Check if LG exists, update title if needed, or create
            learning_goal = db.session.query(LearningGoal).get(lg_id)
            if not learning_goal:
                learning_goal = LearningGoal(id=lg_id, title=lg_title, subject_id=subject.id)
                db.session.add(learning_goal)
            else:
                learning_goal.title = lg_title
                learning_goal.subject_id = subject.id
            
            db.session.commit()
            
            # Keywords
            current_keywords = []
            for kw_word in lg_data.get('keywords', []):
                keyword = get_or_create(db.session, Keyword, word=kw_word)
                current_keywords.append(keyword)
            
            # Update association
            learning_goal.keywords = current_keywords
            db.session.commit()
            
            # Snapshots
            for snap_data in lg_data.get('snapshots', []):
                source_data = snap_data.get('source', {})
                source_type = source_data.get('type')
                source_id = source_data.get('id')
                date_str = snap_data.get('at')
                
                # Check if snapshot already exists
                snapshot = db.session.query(Snapshot).filter_by(
                    student_id=student.id,
                    learning_goal_id=learning_goal.id,
                    source_type=source_type,
                    source_id=source_id
                ).first()
                
                if not snapshot:
                    snapshot = Snapshot(
                        student_id=student.id,
                        learning_goal_id=learning_goal.id,
                        date=date_str,
                        source_type=source_type,
                        source_id=source_id
                    )
                    db.session.add(snapshot)
                    db.session.commit()
                    
                    # Taxonomy Scores
                    for tax_data in snap_data.get('taxonomy', []):
                        score = TaxonomyScore(
                            snapshot_id=snapshot.id,
                            level=tax_data.get('level'),
                            kennen=tax_data.get('kennen'),
                            kunnen=tax_data.get('kunnen'),
                            confidence=tax_data.get('confidence')
                        )
                        db.session.add(score)
                    db.session.commit()

        print(f"Successfully imported data for student {student.name} in {subject.name}")
        return True
        
    except Exception as e:
        print(f"Error importing data: {e}")
        db.session.rollback()
        return False
