from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRACKS = [
    12,
    143,
    320,
    344,
    496,
    514
]

REGION_DIR = (
    ROOT /
    "generated" /
    "corner_regions"
)

for track_id in TRACKS:

    print()
    print("=" * 60)
    print(track_id)
    print("=" * 60)

    path = (
        REGION_DIR /
        f"{track_id}.json"
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    for idx, corner in enumerate(
        data["corners"],
        start=1
    ):

        width = (
            corner["end_pct"]
            -
            corner["start_pct"]
        )

        if width < 0:
            width += 1.0

        print(
            f"C{idx}: "
            f"width={width:.3f} "
            f"strength={corner['strength']:.6f}"
        )
