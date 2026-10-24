from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REGION_DIR = ROOT / "generated" / "corner_regions"
TRACK_DIR = ROOT / "generated"

registry = []

for region_file in REGION_DIR.glob("*.json"):

    track_id = region_file.stem

    track_file = TRACK_DIR / f"{track_id}.json"

    record = {
        "track_id": int(track_id),
        "knowledge_level": "geometry_only",
        "named_corner_count": 0,
        "generated_corner_count": 0
    }

    with open(
        region_file,
        "r",
        encoding="utf-8"
    ) as f:

        region_data = json.load(f)

    record["generated_corner_count"] = len(
        region_data.get(
            "corners",
            []
        )
    )

    if track_file.exists():

        with open(
            track_file,
            "r",
            encoding="utf-8"
        ) as f:

            track_data = json.load(f)

        named_count = len(
            track_data.get(
                "corners",
                []
            )
        )

        record["named_corner_count"] = named_count

        if named_count > 0:

            record["knowledge_level"] = "direct"

        knowledge_source = track_data.get(
            "knowledge_source"
        )

        if knowledge_source:

            record["knowledge_level"] = "inherited"

            record["parent_track_id"] = (
                knowledge_source.get(
                    "parent_track_id"
                )
            )

            record["inheritance_level"] = (
                knowledge_source.get(
                    "inheritance_level"
                )
            )

    registry.append(record)

registry.sort(
    key=lambda x: x["track_id"]
)

with open(
    ROOT /
    "generated" /
    "knowledge_registry.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        registry,
        f,
        indent=2
    )

print(
    f"Built {len(registry)} records"
)
