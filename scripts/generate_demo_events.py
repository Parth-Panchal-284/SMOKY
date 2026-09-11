"""Demo event scheduler placeholder.

Next milestone: POST these events to /api/reports at timed intervals and trigger
zone re-analysis through RocketRide. For now the static dataset drives the UI.
"""

EVENT_SEQUENCE = [
    (0, "Official flood watch received"),
    (10, "First X report in Z1"),
    (20, "Citizen report corroborates Z1 flooding"),
    (30, "Instagram report adds media evidence"),
    (45, "Responder confirmation raises confidence"),
    (65, "First Z3 flood report"),
    (80, "Z3 receives second independent report"),
    (95, "Z3 becomes CRITICAL"),
]

if __name__ == "__main__":
    for second, event in EVENT_SEQUENCE:
        print(f"T+{second:03d}s  {event}")
