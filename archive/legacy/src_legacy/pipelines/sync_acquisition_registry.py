import json
from pathlib import Path

registry = json.load(
    open(
        "generated/acquisition_registry.json",
        encoding="utf-8"
    )
)

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

updated = 0

for track in catalog:

    track_id = str(
        track["track_id"]
    )

    commentary = (
        Path(track["folder"])
        / "commentary.json"
    )

    if not commentary.exists():
        continue

    data = json.load(
        open(
            commentary,
            encoding="utf-8"
        )
    )

    has_youtube = bool(
        data.get(
            "track_summary",
            {}
        )
    )

    if has_youtube:

        registry[track_id][
            "youtube"
        ]["status"] = "complete"

    updated += 1

with open(
    "generated/acquisition_registry.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        registry,
        f,
        indent=2
    )

print(
    "updated",
    updated,
    "tracks"
)
