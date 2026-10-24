from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ANOMALY_FILE = Path(
    "anomaly_report_v4.csv"
)

REGION_DIR = (
    ROOT /
    "generated" /
    "corner_regions"
)

groups = {}

with open(
    ANOMALY_FILE,
    "r",
    encoding="utf-16"
) as f:

    for row in csv.reader(f):

        if not row:
            continue

        track_id = row[0]
        reason = row[1]

        groups.setdefault(
            reason,
            []
        ).append(
            int(track_id)
        )

print()
print("ANOMALY GROUPS")
print("==============")

for reason, tracks in sorted(
    groups.items()
):

    print()

    print(
        f"{reason}: {len(tracks)}"
    )

    print(
        tracks[:20]
    )
