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

    intervals = []

    for c in data["corners"]:

        start = c["start_pct"]
        end = c["end_pct"]

        if end < start:

            intervals.append(
                (start, 1.0)
            )

            intervals.append(
                (0.0, end)
            )

        else:

            intervals.append(
                (start, end)
            )

    intervals.sort()

    merged = []

    for start, end in intervals:

        if (
            not merged
            or
            start > merged[-1][1]
        ):

            merged.append(
                [start, end]
            )

        else:

            merged[-1][1] = max(
                merged[-1][1],
                end
            )

    coverage = sum(
        end - start
        for start, end in merged
    )

    widest = 0

    for c in data["corners"]:

        width = (
            c["end_pct"]
            -
            c["start_pct"]
        )

        if width < 0:
            width += 1

        widest = max(
            widest,
            width
        )

    print(
        f'{data["track_id"]},'
        f'{len(data["corners"])},'
        f'{coverage:.3f},'
        f'{widest:.3f}'
    )
