import json
from pathlib import Path

packs = Path(
    "generated/knowledge_packs"
)

tracks = 0
corners = 0

for file in packs.glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    tracks += 1

    corners += len(
        data.get(
            "corners",
            []
        )
    )

print(
    "knowledge_packs:",
    tracks
)

print(
    "total_corners:",
    corners
)

print(
    "avg_corners_per_track:",
    round(
        corners / tracks,
        2
    )
)
