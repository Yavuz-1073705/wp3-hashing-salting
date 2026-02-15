from flask import Blueprint, render_template, abort
from app import db
from app.models import Student, Snapshot, LearningGoal

bp = Blueprint('student', __name__)


@bp.route('/')
def landing():
    """Student landing page - shows list of all students."""
    students = Student.query.order_by(Student.name).all()
    return render_template('student/landing.html', students=students)


@bp.route('/dashboard/<int:student_id>')
def dashboard(student_id):
    """Student dashboard - shows progress, learning goals, and keywords for specific student."""
    # Get student from database
    student = db.session.get(Student, student_id)
    if not student:
        abort(404)
    
    # Get all snapshots for this student
    snapshots = Snapshot.query.filter_by(student_id=student.id).all()
    
    # Calculate statistics
    total_snapshots = len(snapshots)
    
    # Get unique learning goals
    learning_goal_ids = set(snap.learning_goal_id for snap in snapshots)
    learning_goals_data = []
    all_keywords = {}
    
    avg_score_total = 0
    weak_points = 0
    
    for lg_id in learning_goal_ids:
        lg = db.session.get(LearningGoal, lg_id)
        if not lg:
            continue
            
        # Get all snapshots for this learning goal
        lg_snapshots = [s for s in snapshots if s.learning_goal_id == lg_id]
        
        # Calculate average kennen and kunnen for this learning goal
        total_kennen = 0
        total_kunnen = 0
        count = 0
        
        for snap in lg_snapshots:
            for tax in snap.taxonomy_scores:
                total_kennen += tax.kennen
                total_kunnen += tax.kunnen
                count += 1
        
        if count > 0:
            avg_kennen = total_kennen / count
            avg_kunnen = total_kunnen / count
            avg_score_total += (avg_kennen + avg_kunnen) / 2
            
            if avg_kunnen < 0.5:
                weak_points += 1
        else:
            avg_kennen = 0
            avg_kunnen = 0
        
        learning_goals_data.append({
            'id': lg.id,
            'title': lg.title,
            'avg_kennen': avg_kennen,
            'avg_kunnen': avg_kunnen
        })
        
        # Collect keywords for this learning goal
        for keyword in lg.keywords:
            if keyword.word not in all_keywords:
                all_keywords[keyword.word] = {'scores': [], 'word': keyword.word}
            all_keywords[keyword.word]['scores'].append((avg_kennen + avg_kunnen) / 2)
    
    # Calculate average keyword scores
    keywords_data = []
    for word, data in all_keywords.items():
        avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
        status = 'strong' if avg_score >= 0.75 else ('moderate' if avg_score >= 0.5 else 'weak')
        keywords_data.append({
            'word': word,
            'avg_score': avg_score,
            'status': status
        })
    
    # Calculate overall average score
    avg_score = int((avg_score_total / len(learning_goal_ids) * 100)) if learning_goal_ids else 0
    
    stats = {
        'total_snapshots': total_snapshots,
        'avg_score': avg_score,
        'learning_goals': len(learning_goal_ids),
        'weak_points': weak_points
    }
    
    return render_template('student/dashboard.html',
                         student=student,
                         stats=stats,
                         learning_goals=learning_goals_data,
                         keywords=keywords_data)
