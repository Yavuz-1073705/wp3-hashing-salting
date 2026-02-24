from app import db
from app.models import Student, LearningGoal, Snapshot

TAXONOMY_ORDER = ['Onthouden', 'Begrijpen', 'Toepassen', 'Analyseren']


def get_class_overview():
    """
    Aggregates all snapshot data to produce a class-level overview.
    Returns per-student averages, per-learning-goal averages,
    per-taxonomy-level averages and per-keyword averages.
    """
    goal_stats = {}
    taxonomy_stats = {}

    all_snapshots = Snapshot.query.all()

    for snap in all_snapshots:
        lg = db.session.get(LearningGoal, snap.learning_goal_id)
        if not lg:
            continue

        scores = list(snap.taxonomy_scores)
        if not scores:
            continue

        lg_id = snap.learning_goal_id
        if lg_id not in goal_stats:
            goal_stats[lg_id] = {
                'id': lg.id,
                'title': lg.title,
                'subject': lg.subject.name if lg.subject else '',
                'keywords': [k.word for k in lg.keywords],
                'kennen_sum': 0.0,
                'kunnen_sum': 0.0,
                'count': 0,
                'students': set(),
            }

        for t in scores:
            goal_stats[lg_id]['kennen_sum'] += t.kennen
            goal_stats[lg_id]['kunnen_sum'] += t.kunnen
            goal_stats[lg_id]['count'] += 1

            level = t.level
            if level not in taxonomy_stats:
                taxonomy_stats[level] = {'kennen_sum': 0.0, 'kunnen_sum': 0.0, 'count': 0}
            taxonomy_stats[level]['kennen_sum'] += t.kennen
            taxonomy_stats[level]['kunnen_sum'] += t.kunnen
            taxonomy_stats[level]['count'] += 1

        goal_stats[lg_id]['students'].add(snap.student_id)

    # Per-student averages
    students = Student.query.order_by(Student.name).all()
    student_data = []
    for student in students:
        snapshots = Snapshot.query.filter_by(student_id=student.id).all()
        ken_sum = 0.0
        kun_sum = 0.0
        total = 0

        for snap in snapshots:
            for t in snap.taxonomy_scores:
                ken_sum += t.kennen
                kun_sum += t.kunnen
                total += 1

        student_data.append({
            'id': student.id,
            'name': student.name,
            'avg_kennen': round(ken_sum / total, 3) if total else 0,
            'avg_kunnen': round(kun_sum / total, 3) if total else 0,
            'snapshot_count': len(snapshots),
        })

    # Build learning goals list sorted by avg kunnen ascending (weakest first)
    learning_goals = []
    for g in goal_stats.values():
        c = g['count']
        learning_goals.append({
            'id': g['id'],
            'title': g['title'],
            'subject': g['subject'],
            'keywords': g['keywords'],
            'avg_kennen': round(g['kennen_sum'] / c, 3) if c else 0,
            'avg_kunnen': round(g['kunnen_sum'] / c, 3) if c else 0,
            'student_count': len(g['students']),
        })
    learning_goals.sort(key=lambda x: x['avg_kunnen'])

    # Keyword aggregation: average of all goals that contain each keyword
    keyword_scores = {}
    for g in learning_goals:
        avg = (g['avg_kennen'] + g['avg_kunnen']) / 2
        for word in g['keywords']:
            if word not in keyword_scores:
                keyword_scores[word] = {'sum': 0.0, 'count': 0}
            keyword_scores[word]['sum'] += avg
            keyword_scores[word]['count'] += 1

    keywords_list = []
    for word, d in keyword_scores.items():
        keywords_list.append({
            'word': word,
            'avg_score': round(d['sum'] / d['count'], 3) if d['count'] else 0,
        })
    keywords_list.sort(key=lambda x: x['avg_score'])

    # Taxonomy levels in fixed order
    taxonomy_list = []
    for level in TAXONOMY_ORDER:
        d = taxonomy_stats.get(level, {'kennen_sum': 0, 'kunnen_sum': 0, 'count': 0})
        c = d['count']
        taxonomy_list.append({
            'level': level,
            'avg_kennen': round(d['kennen_sum'] / c, 3) if c else 0,
            'avg_kunnen': round(d['kunnen_sum'] / c, 3) if c else 0,
        })

    # Summary stats
    all_kunnen = [s['avg_kunnen'] for s in student_data if s['snapshot_count'] > 0]
    class_avg = round(sum(all_kunnen) / len(all_kunnen), 3) if all_kunnen else 0
    weak_goals = sum(1 for g in learning_goals if g['avg_kunnen'] < 0.5)
    problem_kw = sum(1 for k in keywords_list if k['avg_score'] < 0.5)

    return {
        'stats': {
            'total_students': len(students),
            'class_avg_kunnen': class_avg,
            'weak_goals_count': weak_goals,
            'problem_keywords_count': problem_kw,
        },
        'students': sorted(student_data, key=lambda x: x['avg_kunnen']),
        'learning_goals': learning_goals,
        'taxonomy_levels': taxonomy_list,
        'keywords': keywords_list[:20],
    }
