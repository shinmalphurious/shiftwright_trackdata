from __future__ import annotations

import json
from pathlib import Path

TRACK_ID = 427

ROOT = Path(__file__).resolve().parents[2]

FILE = (
    ROOT /
    "generated" /
    "corner_regions" /
    f"{TRACK_ID}.json"
)

with open(
    FILE,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)

corners = data["corners"]

for i, a in enumerate(corners):

    for j, b in enumerate(corners):

        if j <= i:
            continue

        overlap = (
            a["start_pct"] < b["end_pct"]
            and
            b["start_pct"] < a["end_pct"]
        )

        if overlap:

            print()

            print(
                f"C{i+1} overlaps C{j+1}"
            )

            print(
                f'  {a["start_pct"]:.6f}'
                f' -> '
                f'{a["end_pct"]:.6f}'
            )

            print(
                f'  {b["start_pct"]:.6f}'
                f' -> '
                f'{b["end_pct"]:.6f}'
            )
