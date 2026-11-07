"""Run once: loads the fake company history into Hindsight."""
from memory import remember
from seed_data import INCIDENTS, TRIBAL_KNOWLEDGE, incident_to_text

for inc in INCIDENTS:
    remember(incident_to_text(inc), context="past incident", timestamp=inc["date"])
    print("retained", inc["id"])

for who, note in TRIBAL_KNOWLEDGE:
    remember(f"Tribal knowledge from {who}: {note}", context="tribal knowledge")
    print("retained note from", who)

print("Done. Memory is ready.")
