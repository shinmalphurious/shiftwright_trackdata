from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

results = []

with open(
    "alignment_candidates.csv",
    "r",
    encoding="utf-16"
) as f:

    for row in csv.reader(f):

        if not row:
            continue

        track_id = int(row[0])
        parent_id = int(row[1])
        level = row[2]

        generated = int(row[3])
        named = int(row[4])
        diff = int(row[5])

        if diff <= 1:
            confidence = "very_high"
        elif diff <= 2:
            confidence = "high"
        else:
            confidence = "medium"

        results.append(
            {
                "track_id": track_id,
                "parent_track_id": parent_id,
                "inheritance_level": level,
                "generated_corner_count": generated,
                "parent_named_corner_count": named,
                "corner_count_difference": diff,
                "inheritance_confidence": confidence
            }
        )

with open(
    ROOT /
    "generated" /
    "inheritance_registry.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2
    )

print(
    f"Built {len(results)} records"
)
