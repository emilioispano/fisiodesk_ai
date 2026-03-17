from typing import Any, Dict, List

from app.db import get_db, load_patients_map, load_recent_clinical_docs, load_latest_event_by_patient
from app.models import ClinicalEvidence, PatientResult
from app.scoring import score_low_back_pain, score_improvement


def build_clinical_evidences(db) -> List[ClinicalEvidence]:
    docs = load_recent_clinical_docs(db)
    evidences: List[ClinicalEvidence] = []

    for doc in docs:
        text = doc["text"]
        lbp = score_low_back_pain(text)
        improvement = score_improvement(text)

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


def run_query(condition=None, time_window=None, trend=None) -> List[PatientResult]:
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

        has_lbp = lbp_score >= 1.0
        has_improvement = improvement_score >= 1.0
        latest_is_no_show = latest_event.get("stato") == "no_show"

        if has_lbp and has_improvement and latest_is_no_show:
            full_name = f'{patient.get("nome", "")} {patient.get("cognome", "")}'.strip()

            evidence_samples = [
                #ev.text[:140] + ("..." if len(ev.text) > 140 else "") for ev in sorted(agg["evidences"], key=lambda x: x.date, reverse=True)
                ev.text for ev in sorted(agg["evidences"], key=lambda x: x.date, reverse=True)
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
