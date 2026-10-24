from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

with open(
    ROOT / "registry" / "road_tracks.json",
    "r",
    encoding="utf-8"
) as f:

    roads = {
        str(item["track_id"])
        for item in json.load(f)
    }

REGION_DIR = (
    ROOT /
    "generated" /
    "corner_regions"
)

for file in sorted(
    REGION_DIR.glob("*.json")
):

    track_id = file.stem

    if track_id not in roads:
        continue

    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    coverage = 0.0
    widest = 0.0

    for c in data["corners"]:

        width = (
            c["end_pct"]
            -
            c["start_pct"]
        )

        if width < 0:
            width += 1

        coverage += width
        widest = max(
            widest,
            width
        )

    print(
        f"{track_id},"
        f"{len(data['corners'])},"
        f"{coverage:.3f},"
        f"{widest:.3f}"
    )
