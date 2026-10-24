import json
from pathlib import Path

INPUT_DIR = Path(
    "generated"
)

OUTPUT_DIR = Path(
    "generated"
)

updated = 0

for file in INPUT_DIR.glob("*.json"):

    with open(
        file,
        encoding="utf-8"
    ) as fp:

        track = json.load(fp)

    track_length = (
        track.get(
            "metadata",
            {}
        ).get(
            "length_m"
        )
    )

    if not track_length:
        continue

    for corner in track.get(
        "corners",
        []
    ):

        start_pct = corner.get(
            "start_pct"
        )

        end_pct = corner.get(
            "end_pct"
        )

        if (
            start_pct is None
            or end_pct is None
        ):
            continue

        length_pct = (
            end_pct - start_pct
        )

        length_m = (
            track_length
            * length_pct
        )

        corner[
            "corner_length_pct"
        ] = round(
            length_pct,
            4
        )

        corner[
            "corner_length_m"
        ] = round(
            length_m,
            1
        )

    with open(
        file,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            track,
            fp,
            indent=2
        )

    updated += 1

print(
    f"Updated {updated} tracks"
)
