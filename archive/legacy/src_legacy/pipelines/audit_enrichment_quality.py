from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRACK_DIR = ROOT / "generated"
REGION_DIR = ROOT / "generated" / "corner_regions"
DEP_DIR = ROOT / "generated" / "corner_dependencies"

perfect = 0
partial = 0
broken = 0

for file in REGION_DIR.glob("*.json"):

    track_id = file.stem

    knowledge_file = (
        TRACK_DIR /
        f"{track_id}.json"
    )

    dep_file = (
        DEP_DIR /
        f"{track_id}.json"
    )

    if (
        not knowledge_file.exists()
        or
        not dep_file.exists()
    ):
        continue

    with open(
        knowledge_file,
        "r",
        encoding="utf-8"
    ) as f:
        track = json.load(f)

    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:
        regions = json.load(f)

    with open(
        dep_file,
        "r",
        encoding="utf-8"
    ) as f:
        deps = json.load(f)

    named_count = len(
        track.get(
            "corners",
            []
        )
    )

    generated_count = len(
        regions.get(
            "corners",
            []
        )
    )

    dependency_count = len(
        deps.get(
            "dependencies",
            []
        )
    )

    if (
        named_count ==
        generated_count ==
        dependency_count
    ):
        perfect += 1

    elif (
        named_count > 0
        and
        dependency_count > 0
    ):
        partial += 1

    else:
        broken += 1

print()
print(f"perfect: {perfect}")
print(f"partial: {partial}")
print(f"broken : {broken}")