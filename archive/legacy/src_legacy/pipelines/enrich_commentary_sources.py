import json
from pathlib import Path

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

updated = 0

for track in catalog:

    commentary_path = (
        Path(track["folder"])
        / "commentary.json"
    )

    if not commentary_path.exists():
        continue

    commentary = json.load(
        open(
            commentary_path,
            encoding="utf-8"
        )
    )

    track_id = str(
        track["track_id"]
    )

    generated_track = Path(
        f"generated/{track_id}.json"
    )

    commentary.setdefault(
        "available_sources",
        {}
    )

    commentary["available_sources"][
        "geometry"
    ] = track[
        "has_active_svg"
    ]

    commentary["available_sources"][
        "turns"
    ] = track[
        "has_turns_svg"
    ]

    commentary["available_sources"][
        "commentary"
    ] = True

    commentary["available_sources"][
        "corner_data"
    ] = generated_track.exists()

    with open(
        commentary_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            commentary,
            f,
            indent=2
        )

    updated += 1

print(
    "updated",
    updated,
    "tracks"
)
