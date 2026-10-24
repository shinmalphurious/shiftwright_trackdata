from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = (
    ROOT /
    "generated" /
    "corner_regions"
)

for file in sorted(
    INPUT_DIR.glob("*.json")
):

    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    widest = 0.0

    for corner in data["corners"]:

        width = (
            corner["end_pct"]
            - corner["start_pct"]
        )

        if width < 0:
            width += 1.0

        widest = max(
            widest,
            width
        )

    print(
        f'{data["track_id"]},{widest:.3f}'
    )
