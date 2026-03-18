from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pymongo import MongoClient

from app.config import MONGO_URI, DB_NAME, WINDOW_START, REFERENCE_DATE


def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


def load_patients_map(db) -> Dict[str, Dict[str, Any]]:
    patients = list(db.pazienti.find({}))
    return {str(p["_id"]): p for p in patients}


def load_recent_clinical_docs(db, time_window: Optional[Tuple[datetime, datetime]] = None) -> List[Dict[str, Any]]:
    if time_window is None:
        start_date, end_date = WINDOW_START, REFERENCE_DATE
    else:
        start_date, end_date = time_window

    print(f"Start: {start_date}")
    print(f"End: {end_date}")

    valuation_docs = list(
        db.schede_valutazione.find(
            {"data": {"$gte": start_date, "$lt": end_date}}
        )
    )
    treatment_docs = list(
        db.diario_trattamenti.find(
            {"data": {"$gte": start_date, "$lt": end_date}}
        )
    )

    docs = []
    for doc in valuation_docs:
        docs.append({
            "patient_id": str(doc["paziente_id"]),
            "source": "scheda_valutazione",
            "date": doc["data"],
            "text": doc.get("descrizione", ""),
        })

    for doc in treatment_docs:
        docs.append({
            "patient_id": str(doc["paziente_id"]),
            "source": "diario_trattamenti",
            "date": doc["data"],
            "text": doc.get("descrizione", ""),
        })

    return docs


def load_latest_event_by_patient(db, time_window: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Dict[str, Any]]:
    if time_window is None:
        start_date, end_date = WINDOW_START, REFERENCE_DATE
    else:
        start_date, end_date = time_window

    pipeline = [
        {"$match": {"data": {"$gte": start_date, "$lt": end_date}}},
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
