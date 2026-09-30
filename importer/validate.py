import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

all_events = set()
all_votes = set()

for year in ("202223", "202324", "202425", "202526"):
    events = set()
    votes = set()
    raw_count = 0

    for path in (DATA_DIR / year).glob("*.json"):
        with open(path) as f:
            data = json.load(f)

        rows = data["dokvotering"]["votering"]
        raw_count += len(rows)

        for vote in rows:
            events.add(vote["votering_id"])
            votes.add((vote["votering_id"], vote["intressent_id"]))

    all_events.update(events)
    all_votes.update(votes)

    print(f"{year}:")
    print(f"  Voting events: {len(events)}")
    print(f"  Unique votes:  {len(votes)}")
    print(f"  Raw JSON rows: {raw_count}")

print("\nTOTAL:")
print("Voting events:", len(all_events))
print("Unique votes: ", len(all_votes))
