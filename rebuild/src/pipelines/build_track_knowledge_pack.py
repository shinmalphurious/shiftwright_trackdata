import json
from pathlib import Path

OUTDIR = Path(
    "generated/knowledge_packs"
)

OUTDIR.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for source in Path(
    "generated"
).glob("*.json"):

    try:
        track_id = int(source.stem)
    except:
        continue

    track = json.load(
        open(
            source,
            encoding="utf-8"
        )
    )

    region_file = Path(
        f"generated/corner_regions/{track_id}.json"
    )

    corner_regions = {}

    if region_file.exists():

        corner_regions = json.load(
            open(
                region_file,
                encoding="utf-8"
            )
        )

    pack = {

        "track_id": track_id,

        "knowledge_level":
            "named"
            if track.get("corners")
            else "geometry_only",

        "named_corners":
            track.get(
                "corners",
                []
            ),

        "generated_corner_regions":
            corner_regions.get(
                "corners",
                []
            ),

        "youtube_summary": {},

        "turn_consensus": {},

        "metadata":
            track.get(
                "metadata",
                {}
            )
    }

    with open(
        OUTDIR /
        f"{track_id}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            pack,
            f,
            indent=2
        )

    built += 1

print(
    "knowledge packs:",
    built
)
