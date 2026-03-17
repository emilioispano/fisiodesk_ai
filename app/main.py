from datetime import datetime, timezone
from app.services import run_query


def prompt_user():
    print("=== FisioDesk Smart Query ===\n")

    print("Seleziona la patologia:")
    print("1) Lombalgia")
    condition_choice = input("> ").strip()

    print("\nSeleziona intervallo temporale:")
    print("1) Ultimi 3 mesi (fino al 31/12/2024)")
    time_choice = input("> ").strip()

    print("\nSeleziona andamento clinico:")
    print("1) Miglioramento")
    trend_choice = input("> ").strip()

    if condition_choice != "1" or time_choice != "1" or trend_choice != "1":
        print("\nScelta non valida: uso configurazione di default.\n")

    return {
        "condition": "lombalgia",
        "time_window": (
            datetime(2024, 10, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
        "trend": "improvement",
        "latest_event_status": "no_show",
    }


def main():
    params = prompt_user()

    matches = run_query(
        condition=params["condition"],
        time_window=params["time_window"],
        trend=params["trend"],
        latest_event_status=params["latest_event_status"],
    )

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


if __name__ == "__main__":
    main()
