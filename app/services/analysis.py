from collections import defaultdict

from app import db
from app.models import Student, LearningGoal, Snapshot, TaxonomyScore

TAXONOMY_ORDER = ['Onthouden', 'Begrijpen', 'Toepassen', 'Analyseren']


def get_class_overview():
    """
    Aggregates all snapshot data to produce a class-level overview.
    Returns per-student averages, per-learning-goal averages,
    per-taxonomy-level averages and per-keyword averages.

    Uses bulk queries to avoid N+1 query problems.
    """
    all_snapshots = Snapshot.query.all()

    if not all_snapshots:
        return {
            'stats': {
                'total_students': 0,
                'class_avg_kunnen': 0,
                'weak_goals_count': 0,
                'problem_keywords_count': 0,
            },
            'students': [],
            'learning_goals': [],
            'taxonomy_levels': [
                {'level': lvl, 'avg_kennen': 0, 'avg_kunnen': 0}
                for lvl in TAXONOMY_ORDER
            ],
            'keywords': [],
        }

    snap_ids = [s.id for s in all_snapshots]
    lg_ids = list(set(s.learning_goal_id for s in all_snapshots))

    # Bulk-load taxonomy scores
    all_tax = TaxonomyScore.query.filter(TaxonomyScore.snapshot_id.in_(snap_ids)).all()
    scores_by_snap = defaultdict(list)
    for ts in all_tax:
        scores_by_snap[ts.snapshot_id].append(ts)

    # Bulk-load learning goals with their subjects and keywords
    all_lgs = LearningGoal.query.filter(LearningGoal.id.in_(lg_ids)).all()
    lg_dict = {lg.id: lg for lg in all_lgs}

    goal_stats = {}
    taxonomy_stats = {}
    # Accumulate per-student scores without additional queries
    student_agg = defaultdict(lambda: {'ken_sum': 0.0, 'kun_sum': 0.0, 'total': 0, 'snap_count': 0})

    for snap in all_snapshots:
        lg = lg_dict.get(snap.learning_goal_id)
        if not lg:
            continue

        scores = scores_by_snap.get(snap.id, [])
        if not scores:
            continue

        student_agg[snap.student_id]['snap_count'] += 1

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

            student_agg[snap.student_id]['ken_sum'] += t.kennen
            student_agg[snap.student_id]['kun_sum'] += t.kunnen
            student_agg[snap.student_id]['total'] += 1

            level = t.level
            if level not in taxonomy_stats:
                taxonomy_stats[level] = {'kennen_sum': 0.0, 'kunnen_sum': 0.0, 'count': 0}
            taxonomy_stats[level]['kennen_sum'] += t.kennen
            taxonomy_stats[level]['kunnen_sum'] += t.kunnen
            taxonomy_stats[level]['count'] += 1

        goal_stats[lg_id]['students'].add(snap.student_id)

    # Per-student averages (no additional DB queries needed)
    students = Student.query.order_by(Student.name).all()
    student_data = []
    for student in students:
        agg = student_agg[student.id]
        student_data.append({
            'id': student.id,
            'name': student.name,
            'avg_kennen': round(agg['ken_sum'] / agg['total'], 3) if agg['total'] else 0,
            'avg_kunnen': round(agg['kun_sum'] / agg['total'], 3) if agg['total'] else 0,
            'snapshot_count': agg['snap_count'],
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
