from datetime import datetime, timezone
from app.services import run_query


def prompt_user():
    # Prompt CLI per navigare la app
    print("=== FisioDesk Smart Query ===\n")

    print("Seleziona la patologia:")
    print("1) Lombalgia")
    print("*) Work In Progress...")
    condition_choice = input("> ").strip()

    print("\nSeleziona la data (precedente il 31/12/2024) per definire il periodo:")
    print("Mese: [1 - 12]")
    month_choice = input("> ").strip()
    print("Giorno: [1 - 31]")
    day_choice = input("> ").strip()

    print("\nSeleziona andamento clinico:")
    print("1) Miglioramento")
    print("2) Peggioramento")
    trend_choice = input("> ").strip()

    print("\nFiltro ultimo appuntamento:")
    print("1) Solo no_show")
    print("2) Nessun filtro")
    event_choice = input("> ").strip()

    # Controlli sull'input
    if condition_choice != "1":
        print("\nScelta patologia non valida: uso configurazione di default (Lombalgia).\n")
        condition_choice = "1"

    if trend_choice not in {"1", "2"}:
        print("\nScelta trend non valida: uso ocnfigurazione di default (Miglioramento).\n")
        trend_choice = "1"
    trend = "worsening" if trend_choice == "2" else "improvement"

    if int(month_choice) < 1 or int(month_choice) > 12:
        print("\nScelta non valida: uso data di default 01/10/2024")
        month_choice = "10"
        day_choice = "1"

    if int(day_choice) < 1:
        print("\nScelta giorno non valida: uso il primo del mese scelto")
        day_choice = "1"

    if month_choice in ["1", "3", "5", "7", "8", "10", "12"] and int(day_choice) > 31:
        print("\nScelta giorno non valida: uso l'ultimo del mese scelto")
        day_choice = "31"

    if month_choice in ["11", "4", "6", "9"] and int(day_choice) > 30:
        print("\nScelta giorno non valida: uso l'ultimo del mese scelto")
        day_choice = "30"

    if month_choice == "2" and int(day_choice) > 28:
        print("\nScelta giorno non valida: uso l'ultimo del mese scelto")
        day_choice = "28"

    latest_event_status = None if event_choice == "2" else "no_show"

    return {
        "condition": "lombalgia",
        "time_window": (
            datetime(2024, int(month_choice), int(day_choice), tzinfo=timezone.utc),
            datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
        "trend": trend,
        "latest_event_status": latest_event_status,
    }


def main():
    params = prompt_user()

    # Passo le scelte alla run_query per estrazione dei dati
    matches = run_query(
        condition=params["condition"],
        time_window=params["time_window"],
        trend=params["trend"],
        latest_event_status=params["latest_event_status"],
    )

    # E stampo i risultati
    print("\n=== QUERY RESULT ===\n")
    for r in matches:
        print(f"- {r.full_name}")
        print(f"  patient_id: {r.patient_id}")
        print(f"  latest_event: {r.latest_event_date} [{r.latest_event_status}]")
        print(f"  lbp_score: {r.lbp_score:.2f}")
        print(f"  improvement_score: {r.improvement_score:.2f}")
        print(f"  worsening_score: {r.worsening_score:.2f}")
        print(f"  evidences: {r.evidence_count}")
        for sample in r.evidence_samples:
            print(f"    • {sample}")
        print()


if __name__ == "__main__":
    main()
