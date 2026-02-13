from flask import Blueprint, render_template

bp = Blueprint('student', __name__)


@bp.route('/')
def landing():
    """Student landing page - login not yet implemented."""
    return render_template('student/landing.html')


@bp.route('/dashboard')
def dashboard():
    """Student dashboard - shows progress, learning goals, and keywords."""
    # Mock data for layout demonstration (no authentication yet)
    mock_student = {
        'id': 12345,
        'name': 'Sam de Student'
    }
    
    mock_stats = {
        'total_snapshots': 42,
        'avg_score': 78,
        'learning_goals': 5,
        'weak_points': 3
    }
    
    # Mock learning goals for placeholder
    mock_learning_goals = [
        {'id': 'LG-1', 'title': 'Fotosynthese uitleggen', 'avg_kennen': 0.85, 'avg_kunnen': 0.70},
        {'id': 'LG-2', 'title': 'Cellen en organellen herkennen', 'avg_kennen': 0.62, 'avg_kunnen': 0.50},
        {'id': 'LG-3', 'title': 'DNA-structuur beschrijven', 'avg_kennen': 0.45, 'avg_kunnen': 0.35}
    ]
    
    # Mock keywords
    mock_keywords = [
        {'word': 'chlorofyl', 'avg_score': 0.82, 'status': 'strong'},
        {'word': 'mitochondriën', 'avg_score': 0.56, 'status': 'moderate'},
        {'word': 'glucose', 'avg_score': 0.43, 'status': 'weak'},
        {'word': 'celkern', 'avg_score': 0.65, 'status': 'moderate'}
    ]
    
    return render_template('student/dashboard.html',
                         student=mock_student,
                         stats=mock_stats,
                         learning_goals=mock_learning_goals,
                         keywords=mock_keywords)
