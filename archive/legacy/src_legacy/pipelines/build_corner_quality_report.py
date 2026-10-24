from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REGION_DIR = (
    ROOT /
    "generated" /
    "corner_regions"
)

for file in sorted(
    REGION_DIR.glob("*.json")
):

    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    count = len(
        data["corners"]
    )

    coverage = 0.0

    widest = 0.0

    for corner in data["corners"]:

        width = (
            corner["end_pct"]
            -
            corner["start_pct"]
        )

        if width < 0:
            width += 1.0

        coverage += width

        widest = max(
            widest,
            width
        )

    print(
        f'{data["track_id"]},'
        f'{count},'
        f'{coverage:.3f},'
        f'{widest:.3f}'
    )

if __name__ == "__main__":
    pass
