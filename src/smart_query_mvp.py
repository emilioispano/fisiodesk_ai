from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Iterable
import re

from pymongo import MongoClient
import os


# =========================
# Configurazione
# =========================

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/fisiodesk?directConnection=true&serverSelectionTimeoutMS=2000")
DB_NAME = "fisiodesk"

# Data di riferimento esplicita consigliata dal dataset
REFERENCE_DATE = datetime(2024, 12, 31, tzinfo=timezone.utc)
WINDOW_START = datetime(2024, 10, 1, tzinfo=timezone.utc)


# =========================
# Vocabolari MVP rule-based
# =========================

LOW_BACK_PATTERNS = [
    r"\bdolore lombare\b",
    r"\blombalgia\b",
    r"\bmal di schiena\b",
    r"\brachialgia lombare\b",
    r"\blow back pain\b",
    r"\bdolore alla bassa schiena\b",
    r"\bcolpo della strega\b",
    r"\bzona lombare\b",
    r"\bmuscolatura lombare\b",
    r"\bcolonna lombare\b",
]

IMPROVEMENT_PATTERNS = [
    r"\bmiglioramento\b",
    r"\bmiglioramento significativo\b",
    r"\bottimi progressi\b",
    r"\bprogressi\b",
    r"\bsegni di recupero\b",
    r"\brecupero\b",
    r"\bnetto miglioramento\b",
    r"\bsta molto meglio\b",
    r"\bmolto meglio\b",
    r"\bsituazione eccellente\b",
    r"\bcompleta risoluzione\b",
    r"\bbuon recupero\b",
    r"\bnessun dolore residuo\b",
    r"\bquasi completamente risolto\b",
    r"\bcompletamente guarito\b",
    r"\bdiminuita sensibilmente\b",
    r"\briduzione\b",
    r"\bridotto a\b",
    r"\bguarito\b",
]

NEGATIVE_IMPROVEMENT_PATTERNS = [
    r"\bstazionaria\b",
    r"\blieve peggioramento\b",
    r"\bpeggioramento\b",
    r"\bnessun miglioramento\b",
]


@dataclass
class MatchEvidence:
    source_collection: str
    record_id: str
    data: str
    text: str


@dataclass
class QueryResult:
    paziente_id: str
    nome: str
    cognome: str
    ultimo_appuntamento_data: str
    ultimo_appuntamento_stato: str
    lombare_match: bool
    miglioramento_match: bool
    evidenze_lombari: list[dict[str, Any]]
    evidenze_miglioramento: list[dict[str, Any]]
    spiegazione: str


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def matches_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def parse_mongo_date(value: Any) -> datetime:
    """
    Gestisce valori datetime già deserializzati da PyMongo.
    """
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    raise TypeError(f"Formato data non supportato: {type(value)}")


def find_textual_evidence(
    records: Iterable[dict[str, Any]],
    source_collection: str,
    patient_id: Any,
    start_date: datetime,
    end_date: datetime,
) -> tuple[list[MatchEvidence], list[MatchEvidence]]:
    """
    Restituisce:
    - evidenze lombari
    - evidenze di miglioramento
    """
    lombare_hits: list[MatchEvidence] = []
    improvement_hits: list[MatchEvidence] = []

    for rec in records:
        if rec.get("paziente_id") != patient_id:
            continue

        record_date = parse_mongo_date(rec["data"])
        if not (start_date <= record_date <= end_date):
            continue

        text = normalize_text(rec.get("descrizione", ""))

        has_low_back = matches_any(text, LOW_BACK_PATTERNS)
        has_improvement = (
            matches_any(text, IMPROVEMENT_PATTERNS)
            and not matches_any(text, NEGATIVE_IMPROVEMENT_PATTERNS)
        )

        evidence = MatchEvidence(
            source_collection=source_collection,
            record_id=str(rec.get("_id")),
            data=record_date.isoformat(),
            text=rec.get("descrizione", ""),
        )

        if has_low_back:
            lombare_hits.append(evidence)

        # Per essere più robusti, consideriamo miglioramento clinicamente rilevante
        # solo se il testo è nello stesso record anche riferito alla regione lombare
        # oppure se abbiamo già un match lombare in quel record.
        if has_improvement and has_low_back:
            improvement_hits.append(evidence)
        elif has_improvement and source_collection == "diario_trattamenti":
            # Nei trattamenti spesso il miglioramento è implicito.
            # Se il testo contiene riferimenti lombari o alla schiena lo accettiamo.
            if matches_any(text, LOW_BACK_PATTERNS):
                improvement_hits.append(evidence)

    return lombare_hits, improvement_hits


def get_last_appointment(events: Iterable[dict[str, Any]], patient_id: Any) -> dict[str, Any] | None:
    patient_events = [e for e in events if e.get("paziente_id") == patient_id]
    if not patient_events:
        return None

    patient_events.sort(key=lambda e: parse_mongo_date(e["data"]), reverse=True)
    return patient_events[0]


def run_query() -> list[QueryResult]:
    client = MongoClient(MONGO_URI)
    client.admin.command("ping")  # fail fast se la connessione non va
    db = client[DB_NAME]

    pazienti = list(db.pazienti.find({}))
    schede = list(db.schede_valutazione.find({}))
    trattamenti = list(db.diario_trattamenti.find({}))
    eventi = list(db.eventi_calendario.find({}))

    results: list[QueryResult] = []

    for paziente in pazienti:
        patient_id = paziente["_id"]

        schede_lombari, schede_improvement = find_textual_evidence(
            schede,
            source_collection="schede_valutazione",
            patient_id=patient_id,
            start_date=WINDOW_START,
            end_date=REFERENCE_DATE,
        )

        tratt_lombari, tratt_improvement = find_textual_evidence(
            trattamenti,
            source_collection="diario_trattamenti",
            patient_id=patient_id,
            start_date=WINDOW_START,
            end_date=REFERENCE_DATE,
        )

        all_lombari = schede_lombari + tratt_lombari
        all_improvement = schede_improvement + tratt_improvement

        has_low_back = len(all_lombari) > 0
        has_improvement = len(all_improvement) > 0

        last_event = get_last_appointment(eventi, patient_id)
        if not last_event:
            continue

        last_event_date = parse_mongo_date(last_event["data"])
        last_event_status = last_event.get("stato")

        last_appointment_missed = last_event_status == "no_show"

        if has_low_back and has_improvement and last_appointment_missed:
            explanation_parts = []

            if all_improvement:
                latest_improvement = sorted(all_improvement, key=lambda x: x.data, reverse=True)[0]
                explanation_parts.append(
                    f"Miglioramento clinico rilevato in {latest_improvement.source_collection} "
                    f"del {latest_improvement.data[:10]}"
                )

            explanation_parts.append(
                f"Ultimo appuntamento del {last_event_date.date().isoformat()} con stato '{last_event_status}'"
            )

            result = QueryResult(
                paziente_id=str(patient_id),
                nome=paziente.get("nome", ""),
                cognome=paziente.get("cognome", ""),
                ultimo_appuntamento_data=last_event_date.isoformat(),
                ultimo_appuntamento_stato=last_event_status,
                lombare_match=has_low_back,
                miglioramento_match=has_improvement,
                evidenze_lombari=[asdict(x) for x in all_lombari],
                evidenze_miglioramento=[asdict(x) for x in all_improvement],
                spiegazione="; ".join(explanation_parts),
            )
            results.append(result)

    results.sort(key=lambda r: (r.cognome, r.nome))
    return results


if __name__ == "__main__":
    matches = run_query()

    print("\n=== RISULTATI QUERY MVP ===\n")
    if not matches:
        print("Nessun paziente trovato.")
    else:
        for idx, item in enumerate(matches, start=1):
            print(f"{idx}. {item.nome} {item.cognome}")
            print(f"   Paziente ID: {item.paziente_id}")
            print(f"   Ultimo appuntamento: {item.ultimo_appuntamento_data}")
            print(f"   Stato ultimo appuntamento: {item.ultimo_appuntamento_stato}")
            print(f"   Spiegazione: {item.spiegazione}")

            if item.evidenze_miglioramento:
                latest = sorted(item.evidenze_miglioramento, key=lambda x: x["data"], reverse=True)[0]
                print(f"   Evidenza miglioramento: {latest['text']}")

            print()
