from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_DIR = ROOT / "generated"
REGION_DIR = ROOT / "generated" / "corner_regions"
DEP_DIR = ROOT / "generated" / "corner_dependencies"

for file in REGION_DIR.glob("*.json"):

    track_id = file.stem

    knowledge_file = (
        KNOWLEDGE_DIR /
        f"{track_id}.json"
    )

    if not knowledge_file.exists():
        continue

    with open(file,"r",encoding="utf-8") as f:
        regions = json.load(f)

    with open(
        knowledge_file,
        "r",
        encoding="utf-8"
    ) as f:
        knowledge = json.load(f)

    with open(
        DEP_DIR / file.name,
        "r",
        encoding="utf-8"
    ) as f:
        deps = json.load(f)

    named_count = len(
        knowledge.get(
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
        named_count != generated_count
        or
        generated_count != dependency_count
    ):

        print(
            f"{track_id},"
            f"{named_count},"
            f"{generated_count},"
            f"{dependency_count}"
        )
