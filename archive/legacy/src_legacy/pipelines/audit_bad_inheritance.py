from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REGISTRY = (
    ROOT /
    "generated" /
    "knowledge_registry.json"
)

with open(
    REGISTRY,
    "r",
    encoding="utf-8"
) as f:

    registry = json.load(f)

for row in registry:

    if row.get(
        "knowledge_level"
    ) != "inherited":
        continue

    named = row.get(
        "named_corner_count",
        0
    )

    generated = row.get(
        "generated_corner_count",
        0
    )

    diff = abs(
        named -
        generated
    )

    if diff >= 5:

        print(
            f'{row["track_id"]},'
            f'{row.get("parent_track_id")},'
            f'{named},'
            f'{generated},'
            f'{diff}'
        )
