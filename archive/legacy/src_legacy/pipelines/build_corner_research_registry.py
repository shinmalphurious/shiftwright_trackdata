import json
from pathlib import Path

TRACKS = {
    127: "Road Atlanta",
    219: "Bathurst",
    485: "Zandvoort",
    525: "Spa"
}

OUTPUT = {}

for track_id,track_name in TRACKS.items():

    file = Path(
        f"generated/{track_id}.json"
    )

    if not file.exists():
        continue

    track = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    corners = []

    for idx,corner in enumerate(
        track.get("corners", []),
        start=1
    ):

        corners.append({
            "corner_index": idx,
            "corner_name": corner["name"],
            "start_pct": corner["start_pct"],
            "end_pct": corner["end_pct"],

            # Research fields
            "youtube_mentions": 0,
            "youtube_turns": [],
            "youtube_facts": [],

            # Future fields
            "community_confidence": 0.0,
            "evidence": []
        })

    OUTPUT[str(track_id)] = {
        "track_name": track_name,
        "corner_count": len(corners),
        "corners": corners
    }

with open(
    "generated/corner_research_registry.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        OUTPUT,
        f,
        indent=2
    )

print(
    "created",
    len(OUTPUT),
    "tracks"
)
