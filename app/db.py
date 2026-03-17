from typing import Any, Dict, List
from pymongo import MongoClient

from app.config import MONGO_URI, DB_NAME, WINDOW_START, REFERENCE_DATE


def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


def load_patients_map(db) -> Dict[str, Dict[str, Any]]:
    patients = list(db.pazienti.find({}))
    return {str(p["_id"]): p for p in patients}


def load_recent_clinical_docs(db) -> List[Dict[str, Any]]:
    valuation_docs = list(
        db.schede_valutazione.find(
            {"data": {"$gte": WINDOW_START, "$lt": REFERENCE_DATE}}
        )
    )
    treatment_docs = list(
        db.diario_trattamenti.find(
            {"data": {"$gte": WINDOW_START, "$lt": REFERENCE_DATE}}
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


def load_latest_event_by_patient(db) -> Dict[str, Dict[str, Any]]:
    pipeline = [
        {"$match": {"data": {"$lt": REFERENCE_DATE}}},
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
