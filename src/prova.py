from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pymongo import MongoClient


# =========================
# CONFIG
# =========================

MONGO_URI = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000"
DB_NAME = "fisiodesk"

REFERENCE_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
WINDOW_START = datetime(2024, 10, 1, tzinfo=timezone.utc)  # ultimi 3 mesi circa


# =========================
# DOMAIN MODELS
# =========================

@dataclass
class ClinicalEvidence:
    patient_id: str
    source: str
    date: datetime
    text: str
    lbp_score: float
    improvement_score: float


@dataclass
class PatientResult:
    patient_id: str
    full_name: str
    latest_event_date: datetime
    latest_event_status: str
    lbp_score: float
    improvement_score: float
    evidence_count: int
    evidence_samples: List[str]


# =========================
# TEXT NORMALIZATION
# =========================

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


# =========================
# LOW BACK PAIN DETECTION
# =========================

LBP_PATTERNS = [
    r"\bdolore lombare\b",
    r"\blombalgia\b",
    r"\bmal di schiena\b",
    r"\brachialgia lombare\b",
    r"\blow back pain\b",
    r"\bdolore alla bassa schiena\b",
    r"\bcolpo della strega\b",
]

NEGATIVE_LBP_CONTEXT = [
    r"\bcervicalgia\b",
    r"\bdolore cervicale\b",
    r"\bspalla\b",
    r"\bspalla congelata\b",
]


def score_low_back_pain(text: str) -> float:
    t = normalize_text(text)

    positive_hits = sum(1 for pattern in LBP_PATTERNS if re.search(pattern, t))
    negative_hits = sum(1 for pattern in NEGATIVE_LBP_CONTEXT if re.search(pattern, t))

    score = positive_hits * 1.0 - negative_hits * 0.4
    return max(score, 0.0)


# =========================
# IMPROVEMENT DETECTION
# =========================

IMPROVEMENT_PATTERNS = [
    r"\bmiglioramento\b",
    r"\bmiglioramento significativo\b",
    r"\bnetto miglioramento\b",
    r"\bottimi progressi\b",
    r"\bsta molto meglio\b",
    r"\bbuon recupero\b",
    r"\bcompleta risoluzione\b",
    r"\bnessun dolore residuo\b",
    r"\briduzione significativa\b",
    r"\bmobilità migliorata\b",
    r"\bsituazione eccellente\b",
]

NON_IMPROVEMENT_PATTERNS = [
    r"\bsituazione stazionaria\b",
    r"\bstazionaria\b",
    r"\blieve peggioramento\b",
    r"\bpeggioramento\b",
    r"\bnessun miglioramento\b",
    r"\bpersistente\b",
]


def extract_pain_scores(text: str) -> List[int]:
    """
    Cerca pattern tipo 8/10, 3/10, VAS 9/10 ecc.
    """
    t = normalize_text(text)
    matches = re.findall(r"\b([0-9]|10)\s*/\s*10\b", t)
    return [int(x) for x in matches]


def score_improvement(text: str) -> float:
    t = normalize_text(text)

    positive_hits = sum(1 for pattern in IMPROVEMENT_PATTERNS if re.search(pattern, t))
    negative_hits = sum(1 for pattern in NON_IMPROVEMENT_PATTERNS if re.search(pattern, t))

    score = positive_hits * 1.0 - negative_hits * 1.2

    pain_values = extract_pain_scores(t)
    if len(pain_values) >= 2 and pain_values[0] > pain_values[-1]:
        score += 1.5

    return score


# =========================
# DB ACCESS
# =========================

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


def load_recent_clinical_docs(db) -> List[Dict[str, Any]]:
    valuation_docs = list(
        db.schede_valutazione.find(
            {"data": {"$gte": WINDOW_START, "$lte": REFERENCE_DATE}}
        )
    )
    treatment_docs = list(
        db.diario_trattamenti.find(
            {"data": {"$gte": WINDOW_START, "$lte": REFERENCE_DATE}}
        )
    )

    docs = []
    for doc in valuation_docs:
        docs.append(
            {
                "patient_id": str(doc["paziente_id"]),
                "source": "scheda_valutazione",
                "date": doc["data"],
                "text": doc.get("descrizione", ""),
            }
        )
    for doc in treatment_docs:
        docs.append(
            {
                "patient_id": str(doc["paziente_id"]),
                "source": "diario_trattamenti",
                "date": doc["data"],
                "text": doc.get("descrizione", ""),
            }
        )

    return docs


def load_patients_map(db) -> Dict[str, Dict[str, Any]]:
    patients = list(db.pazienti.find({}))
    return {str(p["_id"]): p for p in patients}


def load_latest_event_by_patient(db) -> Dict[str, Dict[str, Any]]:
    pipeline = [
        {"$match": {"data": {"$lte": REFERENCE_DATE}}},
        {"$sort": {"paziente_id": 1, "data": -1}},
        {
            "$group": {
                "_id": "$paziente_id",
                "latest_event": {"$first": "$$ROOT"}
            }
        }
    ]
    rows = list(db.eventi_calendario.aggregate(pipeline))
    return {str(row["_id"]): row["latest_event"] for row in rows}


# =========================
# CLINICAL ANALYSIS
# =========================

def build_clinical_evidences(db) -> List[ClinicalEvidence]:
    docs = load_recent_clinical_docs(db)
    evidences: List[ClinicalEvidence] = []

    for doc in docs:
        text = doc["text"]
        lbp = score_low_back_pain(text)
        improvement = score_improvement(text)

        # pre-filtro largo: tieni solo documenti almeno potenzialmente rilevanti
        if lbp > 0 or improvement > 0:
            evidences.append(
                ClinicalEvidence(
                    patient_id=doc["patient_id"],
                    source=doc["source"],
                    date=doc["date"],
                    text=text,
                    lbp_score=lbp,
                    improvement_score=improvement,
                )
            )

    return evidences


def aggregate_patient_scores(evidences: List[ClinicalEvidence]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}

    for ev in evidences:
        if ev.patient_id not in out:
            out[ev.patient_id] = {
                "lbp_score": 0.0,
                "improvement_score": 0.0,
                "evidences": [],
            }

        out[ev.patient_id]["lbp_score"] += ev.lbp_score
        out[ev.patient_id]["improvement_score"] += ev.improvement_score
        out[ev.patient_id]["evidences"].append(ev)

    return out


# =========================
# FINAL QUERY
# =========================

def run_query() -> List[PatientResult]:
    db = get_db()

    patients_map = load_patients_map(db)
    latest_events = load_latest_event_by_patient(db)
    evidences = build_clinical_evidences(db)
    aggregated = aggregate_patient_scores(evidences)

    results: List[PatientResult] = []

    for patient_id, agg in aggregated.items():
        latest_event = latest_events.get(patient_id)
        patient = patients_map.get(patient_id)

        if not latest_event or not patient:
            continue

        lbp_score = agg["lbp_score"]
        improvement_score = agg["improvement_score"]

        # soglie MVP
        has_lbp = lbp_score >= 1.0
        has_improvement = improvement_score >= 1.0
        latest_is_no_show = latest_event.get("stato") == "no_show"

        if has_lbp and has_improvement and latest_is_no_show:
            full_name = f'{patient.get("nome", "")} {patient.get("cognome", "")}'.strip()

            evidence_samples = [
                ev.text[:140] + ("..." if len(ev.text) > 140 else "")
                for ev in sorted(agg["evidences"], key=lambda x: x.date, reverse=True)[:3]
            ]

            results.append(
                PatientResult(
                    patient_id=patient_id,
                    full_name=full_name,
                    latest_event_date=latest_event["data"],
                    latest_event_status=latest_event["stato"],
                    lbp_score=lbp_score,
                    improvement_score=improvement_score,
                    evidence_count=len(agg["evidences"]),
                    evidence_samples=evidence_samples,
                )
            )

    results.sort(key=lambda r: (r.latest_event_date, r.improvement_score), reverse=True)
    return results


# =========================
# CLI
# =========================

if __name__ == "__main__":
    matches = run_query()

    print("\n=== QUERY RESULT ===\n")
    for r in matches:
        print(f"- {r.full_name}")
        print(f"  patient_id: {r.patient_id}")
        print(f"  latest_event: {r.latest_event_date} [{r.latest_event_status}]")
        print(f"  lbp_score: {r.lbp_score:.2f}")
        print(f"  improvement_score: {r.improvement_score:.2f}")
        print(f"  evidences: {r.evidence_count}")
        for sample in r.evidence_samples:
            print(f"    • {sample}")
        print()
