import json
from pathlib import Path

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

rows = []

for track in catalog:

    track_id = str(
        track["track_id"]
    )

    generated_file = Path(
        f"generated/{track_id}.json"
    )

    commentary_file = (
        Path(track["folder"])
        / "commentary.json"
    )

    has_corner_data = False
    has_youtube = False

    if commentary_file.exists():

        try:

            commentary = json.load(
                open(
                    commentary_file,
                    encoding="utf-8"
                )
            )

            has_corner_data = generated_file.exists()

            has_youtube = bool(
                commentary.get(
                    "track_summary",
                    {}
                )
            )

        except:
            pass

    rows.append({

        "track_id":
            track["track_id"],

        "layout":
            track["layout"],

        "geometry":
            track["has_active_svg"],

        "turns":
            track["has_turns_svg"],

        "commentary":
            commentary_file.exists(),

        "corner_data":
            has_corner_data,

        "youtube":
            has_youtube
    })

with open(
    "generated/commentary_coverage.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        rows,
        f,
        indent=2
    )

print(
    "tracks:",
    len(rows)
)
