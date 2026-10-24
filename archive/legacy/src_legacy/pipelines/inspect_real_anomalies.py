from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REGION_DIR = (
    ROOT /
    "generated" /
    "corner_regions"
)

with open(
    "anomaly_report_v4.csv",
    "r",
    encoding="utf-16"
) as f:

    for row in csv.reader(f):

        if not row:
            continue

        track_id = row[0]

        if (
            "high_coverage" not in row[1]
            and
            "wide_corner" not in row[1]
        ):
            continue

        path = (
            REGION_DIR /
            f"{track_id}.json"
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as fp:

            data = json.load(fp)

        max_width = 0

        for c in data["corners"]:

            width = (
                c["end_pct"]
                -
                c["start_pct"]
            )

            if width < 0:
                width += 1

            max_width = max(
                max_width,
                width
            )

        print(
            f"{track_id},"
            f"{len(data['corners'])},"
            f"{max_width:.3f}"
        )
