from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pymongo import MongoClient

from app.config import MONGO_URI, DB_NAME, WINDOW_START, REFERENCE_DATE


def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


def load_patients_map(db):
    # Carica i pazienti come dizionario per _id
    patients = list(db.pazienti.find({}))
    return {str(p["_id"]): p for p in patients}


def load_recent_clinical_docs(db, time_window=None):
    if time_window is None:
        # Se non c'è una scelta esplicita, torna al default
        start_date, end_date = WINDOW_START, REFERENCE_DATE
    else:
        start_date, end_date = time_window

    # Per debug
    print(f"Start: {start_date}")
    print(f"End: {end_date}")

    # Prende solo le schede_valutazione dentro la time window
    valuation_docs = list(
        db.schede_valutazione.find(
            {"data": {"$gte": start_date, "$lt": end_date}}
        )
    )

    # Prende solo i trattamenti dentro la time window
    treatment_docs = list(
        db.diario_trattamenti.find(
            {"data": {"$gte": start_date, "$lt": end_date}}
        )
    )

    # Creo una lista con i dati che servono, globale con valutations e treatments
    docs = []
    # ...valutations organizzate in dizionari
    for doc in valuation_docs:
        docs.append({
            "patient_id": str(doc["paziente_id"]),
            "source": "scheda_valutazione",
            "date": doc["data"],
            "text": doc.get("descrizione", ""),
        })

    # ...descriptions organizzate in dizionari
    for doc in treatment_docs:
        docs.append({
            "patient_id": str(doc["paziente_id"]),
            "source": "diario_trattamenti",
            "date": doc["data"],
            "text": doc.get("descrizione", ""),
        })

    return docs


def load_latest_event_by_patient(db, time_window=None):
    if time_window is None:
        # Se non c'è una scelta esplicita, torna al default
        start_date, end_date = WINDOW_START, REFERENCE_DATE
    else:
        start_date, end_date = time_window

    # Creo una query per fare il pull dal mongoDB con:
    # - time window;
    # - ordinamento per paziente e per data dal più recente
    # - raggruppato per paziente
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

    # Applico la query
    rows = list(db.eventi_calendario.aggregate(pipeline))

    # E restituisco un dizionario con paziente -> last event.
    return {str(row["_id"]): row["latest_event"] for row in rows}
