from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

with open(
    ROOT /
    "generated" /
    "knowledge_registry.json",
    "r",
    encoding="utf-8"
) as f:

    registry = json.load(f)

stats = {
    "total_tracks": 0,
    "direct": 0,
    "inherited": 0,
    "geometry_only": 0
}

for item in registry:

    stats["total_tracks"] += 1

    level = item.get(
        "knowledge_level"
    )

    if level in stats:
        stats[level] += 1

with open(
    ROOT /
    "generated" /
    "knowledge_stats.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        stats,
        f,
        indent=2
    )

print(
    json.dumps(
        stats,
        indent=2
    )
)
