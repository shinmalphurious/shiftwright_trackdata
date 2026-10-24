import json
from pathlib import Path

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

created = 0

for track in catalog:

    commentary = Path(
        track["folder"]
    ) / "commentary.json"

    if commentary.exists():
        continue

    data = {

        "track_id":
            track["track_id"],

        "layout":
            track["layout"],

        "track_summary": {},

        "corner_consensus": {},

        "community_evidence": {},

        "telemetry_patterns": {},

        "garage61_patterns": {},

        "llm_context": {}

    }

    with open(
        commentary,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )

    created += 1

print(
    "created",
    created,
    "commentary files"
)
