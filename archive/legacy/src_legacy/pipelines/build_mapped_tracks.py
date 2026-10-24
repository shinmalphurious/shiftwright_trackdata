from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRACK_DIR = ROOT / "generated"
REGION_DIR = ROOT / "generated" / "corner_regions"

OUT_DIR = (
    ROOT /
    "generated" /
    "mapped_tracks"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CANDIDATES = [
    (486,485),
    (503,501),
    (29,192),
    (148,485),
    (194,192),
    (504,501),
    (510,509),
]

for child_id, parent_id in CANDIDATES:

    child_track = (
        TRACK_DIR /
        f"{child_id}.json"
    )

    parent_track = (
        TRACK_DIR /
        f"{parent_id}.json"
    )

    region_file = (
        REGION_DIR /
        f"{child_id}.json"
    )

    if (
        not child_track.exists()
        or
        not parent_track.exists()
        or
        not region_file.exists()
    ):
        continue

    with open(
        child_track,
        "r",
        encoding="utf-8"
    ) as f:
        child = json.load(f)

    with open(
        parent_track,
        "r",
        encoding="utf-8"
    ) as f:
        parent = json.load(f)

    with open(
        region_file,
        "r",
        encoding="utf-8"
    ) as f:
        regions = json.load(f)

    parent_names = [
        c["name"]
        for c in parent.get(
            "corners",
            []
        )
    ]

    mapped = []

    for i, corner in enumerate(
        regions.get(
            "corners",
            []
        )
    ):

        if i < len(parent_names):
            name = parent_names[i]
        else:
            name = (
                f"Extra Corner {i+1}"
            )

        mapped.append(
            {
                "corner_id": i + 1,
                "name": name,
                "apex_pct": corner["apex_pct"],
                "start_pct": corner["start_pct"],
                "end_pct": corner["end_pct"]
            }
        )

    output = {
        "track_id": child_id,
        "parent_track_id": parent_id,
        "mapped_corner_count": len(mapped),
        "corners": mapped
    }

    with open(
        OUT_DIR /
        f"{child_id}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )

print("complete")
