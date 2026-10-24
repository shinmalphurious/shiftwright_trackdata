from __future__ import annotations

import csv

with open(
    "corner_quality_report.csv",
    "r",
    encoding="utf-16"
) as f:

    for row in csv.reader(f):

        if not row:
            continue

        track_id = row[0]
        count = int(row[1])
        coverage = float(row[2])
        widest = float(row[3])

        reasons = []

        if count <= 2:
            reasons.append(
                "low_corner_count"
            )

        if coverage >= 0.60:
            reasons.append(
                "high_coverage"
            )

        if widest >= 0.25:
            reasons.append(
                "wide_corner"
            )

        if reasons:

            print(
                f"{track_id},"
                f"{'|'.join(reasons)}"
            )
