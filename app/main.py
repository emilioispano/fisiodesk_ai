from app.services import run_query


def prompt_user():
    print("=== FisioDesk Smart Query ===\n")

    # Patologia
    print("Seleziona la patologia:")
    print("1) Lombalgia")
    condition = input("> ").strip()

    # Intervallo temporale
    print("\nSeleziona intervallo temporale:")
    print("1) Ultimi 3 mesi (fino al 31/12/2024)")
    time_window = input("> ").strip()

    # Trend
    print("\nSeleziona tipo di andamento:")
    print("1) Miglioramento")
    trend = input("> ").strip()

    # Validazione minimale (no overkill)
    if condition != "1" or time_window != "1" or trend != "1":
        print("\n[!] Scelta non valida. Uso configurazione di default.\n")

    return {
        "condition": "lombalgia",
        "time_window": ("2024-10-01", "2025-01-01"),
        "trend": "improvement"
    }


def main():
    user_input = prompt_user()

    print("\nEseguo Query...\n")

    matches = run_query(
        condition=user_input["condition"],
        time_window=user_input["time_window"],
        trend=user_input["trend"]
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
