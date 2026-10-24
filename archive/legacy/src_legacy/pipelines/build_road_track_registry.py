from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

with open(
    ROOT / "registry" / "track_categories.json",
    "r",
    encoding="utf-8"
) as f:
    categories = json.load(f)

excluded = {
    "Oval",
    "Dirt Oval",
    "Dirt Road"
}

road_tracks = []

for track_id, info in categories.items():

    if info["category"] in excluded:
        continue

    road_tracks.append(
        {
            "track_id": int(track_id),
            "category": info["category"],
            "venue": info["venue"]
        }
    )

road_tracks.sort(
    key=lambda x: x["track_id"]
)

out = ROOT / "registry" / "road_tracks.json"

with open(
    out,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        road_tracks,
        f,
        indent=2
    )

print(
    f"road tracks: {len(road_tracks)}"
)
