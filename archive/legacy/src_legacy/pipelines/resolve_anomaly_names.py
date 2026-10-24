from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

with open(
    ROOT / "registry" / "tracks.json",
    "r",
    encoding="utf-8"
) as f:
    tracks = json.load(f)

ANOMALIES = [
    12,
    143,
    320,
    344,
    496,
    514,
    156,
    157,
    452,
    497,
    519,
    531,
    577
]

for track_id in ANOMALIES:

    key = str(track_id)

    print()
    print(f"Track ID: {track_id}")

    if key not in tracks:
        print("  NOT FOUND")
        continue

    for entry in tracks[key]:

        venue = entry.get(
            "venue_slug",
            ""
        )

        layout = entry.get(
            "layout_slug",
            ""
        )

        category = entry.get(
            "category",
            ""
        )

        print(
            f"  {venue} | {layout} | {category}"
        )
