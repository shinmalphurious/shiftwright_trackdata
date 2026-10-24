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

    corners = data["corners"]

    overlaps = 0

    for i in range(len(corners)):

        a = corners[i]

        for j in range(i + 1, len(corners)):

            b = corners[j]

            if (
                a["start_pct"] < b["end_pct"]
                and
                b["start_pct"] < a["end_pct"]
            ):
                overlaps += 1

    if overlaps:

        print(
            f'{data["track_id"]},{overlaps}'
        )
