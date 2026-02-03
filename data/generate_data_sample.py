import json
import random
from datetime import date, timedelta

random.seed(42)

students = [
    (1, "Sam"), (2, "Alex"), (3, "Jamie"), (4, "Taylor"), (5, "Robin"),
    (6, "Noah"), (7, "Emma"), (8, "Milan"), (9, "Lotte"), (10, "Daan"),
]

subjects = [
    (12, "Biologie"),
    (21, "Natuurkunde"),
    (22, "Scheikunde"),
    (31, "Wiskunde"),
]

taxonomy_scale = ["Onthouden", "Begrijpen", "Toepassen", "Analyseren"]

# Learning goals per subject (subject id -> list of goals)
subject_learning_goals = {
    12: [  # Biologie
        {
            "id": "LG-B-1",
            "title": "Fotosynthese uitleggen",
            "keywords": ["chlorofyl", "glucose", "CO2", "zuurstof"],
        },
        {
            "id": "LG-B-2",
            "title": "Cellen en organellen herkennen",
            "keywords": ["celkern", "mitochondriën", "celmembraan"],
        },
        {
            "id": "LG-B-3",
            "title": "DNA en erfelijkheid beschrijven",
            "keywords": ["DNA", "gen", "chromosoom", "erfelijkheid"],
        },
        {
            "id": "LG-B-4",
            "title": "Ecosystemen analyseren",
            "keywords": ["ecosysteem", "voedselketen", "producent", "consument"],
        },
    ],
    21: [  # Natuurkunde
        {
            "id": "LG-N-1",
            "title": "Beweging en snelheid beschrijven",
            "keywords": ["snelheid", "versnelling", "kracht"],
        },
        {
            "id": "LG-N-2",
            "title": "Energie en behoud verklaren",
            "keywords": ["energie", "arbeid", "behoud"],
        },
        {
            "id": "LG-N-3",
            "title": "Elektrische circuits analyseren",
            "keywords": ["stroom", "spanning", "weerstand"],
        },
        {
            "id": "LG-N-4",
            "title": "Golven en geluid begrijpen",
            "keywords": ["frequentie", "amplitude", "trilling"],
        },
    ],
    22: [  # Scheikunde
        {
            "id": "LG-S-1",
            "title": "Atomaire structuur uitleggen",
            "keywords": ["atoom", "elektron", "proton", "neutron"],
        },
        {
            "id": "LG-S-2",
            "title": "Chemische bindingen herkennen",
            "keywords": ["ionbinding", "covalent", "metaalbinding"],
        },
        {
            "id": "LG-S-3",
            "title": "Reacties en reactiemechanismen",
            "keywords": ["oxidatie", "reductie", "reactiesnelheid"],
        },
        {
            "id": "LG-S-4",
            "title": "Zuren en basen classificeren",
            "keywords": ["pH", "zuur", "base", "neutralisatie"],
        },
    ],
    31: [  # Wiskunde
        {
            "id": "LG-W-1",
            "title": "Algebraïsche vergelijkingen oplossen",
            "keywords": ["x", "vergelijking", "variabele"],
        },
        {
            "id": "LG-W-2",
            "title": "Functies en grafieken interpreteren",
            "keywords": ["functie", "grafiek", "asymptoot"],
        },
        {
            "id": "LG-W-3",
            "title": "Meetkunde: eigenschappen en bewijs",
            "keywords": ["hoek", "driehoek", "bewijs"],
        },
        {
            "id": "LG-W-4",
            "title": "Statistiek en kansberekening",
            "keywords": ["gemiddelde", "mediaan", "kans"],
        },
    ],
}

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def make_taxonomy_block(base_kennen, base_kunnen):
    # Maak per niveau kleine variaties rond een basis
    result = []
    for i, level in enumerate(taxonomy_scale):
        kennen = clamp(base_kennen + random.uniform(-0.15, 0.15) - 0.05 * i)
        kunnen = clamp(base_kunnen + random.uniform(-0.15, 0.15) - 0.07 * i)
        confidence = clamp(0.5 + random.uniform(-0.2, 0.2))
        result.append(
            {
                "level": level,
                "kennen": round(kennen, 2),
                "kunnen": round(kunnen, 2),
                "confidence": round(confidence, 2),
            }
        )
    return result

# Create a shared pool of snapshot sources (date + source metadata).
# The pool is reused by multiple students so snapshots may reference the same source.
def create_source_pool(n=60):
    types = ["quiz", "test", "observatie", "project"]
    base_date = date(2025, 9, 1)
    pool = []
    for i in range(n):
        source_type = random.choice(types)
        day_offset = random.randint(0, 120)
        d = base_date + timedelta(days=day_offset)
        source_id = f"{source_type[:2].upper()}-{random.randint(1, 200)}"
        pool.append({"at": d.isoformat(), "source": {"type": source_type, "id": source_id}})
    return pool

# Instantiate the global source pool once (deterministic thanks to the module-level seed)
SOURCE_POOL = create_source_pool()

def make_snapshots():
    # 1–3 momentopnames per leerdoel. Reuse source metadata from SOURCE_POOL but
    # generate taxonomy measurements per student/snapshot so the same source can be
    # shared while scores differ.
    n = random.randint(1, 3)
    chosen = random.sample(SOURCE_POOL, n)
    snapshots = []
    for src in chosen:
        base_kennen = random.uniform(0.3, 0.9)
        base_kunnen = random.uniform(0.2, 0.8)
        snapshots.append(
            {
                "at": src["at"],
                "source": src["source"],
                "taxonomy": make_taxonomy_block(base_kennen, base_kunnen),
            }
        )
    return snapshots

def make_entry(idx):
    student_id, student_name = random.choice(students)
    subject_id, subject_name = random.choice(subjects)

    # kies 2–4 leerdoelen uit de set die hoort bij het gekozen vak
    goals_for_subject = subject_learning_goals.get(subject_id, [])
    k = random.randint(2, min(len(goals_for_subject), 4))
    goals = random.sample(goals_for_subject, k=k)

    lg_list = []
    for g in goals:
        lg_list.append(
            {
                "id": g["id"],
                "title": g["title"],
                "keywords": g["keywords"],
                "snapshots": make_snapshots(),
            }
        )

    return {
        "student": {"id": student_id, "name": student_name},
        "subject": {"id": subject_id, "name": subject_name},
        "taxonomyScale": taxonomy_scale,
        "learningGoals": lg_list,
    }

def main():
    entries = [make_entry(i) for i in range(40000)]
    with open("data-sample.json", "w", encoding="utf-8") as f:
        json.dump({"entries": entries}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()