from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

with open(
    ROOT / "generated" / "knowledge_registry.json",
    "r",
    encoding="utf-8"
) as f:
    registry = json.load(f)

for item in registry:

    if item.get("knowledge_level") != "inherited":
        continue

    print(
        f'{item["track_id"]},'
        f'{item.get("parent_track_id")},'
        f'{item.get("inheritance_level","unknown")},'
        f'{item["generated_corner_count"]},'
        f'{item["named_corner_count"]}'
    )
