import json
from pathlib import Path

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

available = []
missing = []

for track in catalog:

    track_id = str(
        track["track_id"]
    )

    source = Path(
        f"generated/{track_id}.json"
    )

    if source.exists():

        available.append(
            track["track_id"]
        )

    else:

        missing.append(
            track["track_id"]
        )

print(
    "available_models:",
    len(available)
)

print(
    "missing_models:",
    len(missing)
)
