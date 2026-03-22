from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.db import get_db, load_patients_map, load_recent_clinical_docs, load_latest_event_by_patient
from app.models import ClinicalEvidence, PatientResult
from app.scoring import score_low_back_pain, score_improvement, score_worsening


# Salva una lista delle descrizionin a supporto della scelta
def build_clinical_evidences(db, time_window=None):
    docs = load_recent_clinical_docs(db, time_window=time_window)
    evidences = []

    for doc in docs:
        text = doc["text"]
        lbp = score_low_back_pain(text)
        improvement = score_improvement(text)
        worsening = score_worsening(text)

        if lbp > 0 or improvement > 0 or worsening > 0:
            evidences.append(
                ClinicalEvidence(
                    patient_id=doc["patient_id"],
                    source=doc["source"],
                    date=doc["date"],
                    text=text,
                    lbp_score=lbp,
                    improvement_score=improvement,
                    worsening_score=worsening,
                )
            )

    return evidences


# Per per pazienti con più eventi, li accorpo
def aggregate_patient_scores(evidences):
    out = {}

    for ev in evidences:
        if ev.patient_id not in out:
            out[ev.patient_id] = {
                "lbp_score": 0.0,
                "improvement_score": 0.0,
                "worsening_score": 0.0,
                "evidences": [],
            }

        out[ev.patient_id]["lbp_score"] += ev.lbp_score
        out[ev.patient_id]["improvement_score"] += ev.improvement_score
        out[ev.patient_id]["worsening_score"] += ev.worsening_score
        out[ev.patient_id]["evidences"].append(ev)

    return out


# Qua avviene la ricerca vera e propria "targettizzata" alle scelte fatte in input
# Lascio i default per failsafe
def run_query(condition="lombalgia", time_window=None, trend="improvement", latest_event_status="no_show"):
    db = get_db()

    patients_map = load_patients_map(db)
    latest_events = load_latest_event_by_patient(db, time_window=time_window)
    evidences = build_clinical_evidences(db, time_window=time_window)
    aggregated = aggregate_patient_scores(evidences)

    results = []

    for patient_id, agg in aggregated.items():
        latest_event = latest_events.get(patient_id)
        patient = patients_map.get(patient_id)

        if not latest_event or not patient:
            continue

        lbp_score = agg["lbp_score"]
        improvement_score = agg["improvement_score"]
        worsening_score = agg["worsening_score"]

        # Soglie iniziali per la decisione: 1.0
        # -> è andata bene, funziona gia
        if condition == "lombalgia" and lbp_score < 1.0:
            continue

        if trend == "improvement" and improvement_score < 1.0:
            continue

        if trend == "worsening" and worsening_score < 1.0:
            continue

        if latest_event_status is not None and latest_event.get("stato") != latest_event_status:
            continue

        full_name = f'{patient.get("nome", "")} {patient.get("cognome", "")}'.strip()

        # Se troppo lunghe, qua posso limitarle a N caratteri
        # evidence_samples = [ev.text[:N] for ev in sorted(agg["evidences"], key=lambda x: x.date, reverse=True)]
        evidence_samples = [ev.text for ev in sorted(agg["evidences"], key=lambda x: x.date, reverse=True)]

        results.append(
            PatientResult(
                patient_id=patient_id,
                full_name=full_name,
                latest_event_date=latest_event["data"],
                latest_event_status=latest_event["stato"],
                lbp_score=lbp_score,
                improvement_score=improvement_score,
                worsening_score=worsening_score,
                evidence_count=len(agg["evidences"]),
                evidence_samples=evidence_samples,
            )
        )

    if trend == "worsening":
        results.sort(key=lambda r: (r.latest_event_date, r.worsening_score), reverse=True)
    else:
        results.sort(key=lambda r: (r.latest_event_date, r.improvement_score), reverse=True)

    return results
