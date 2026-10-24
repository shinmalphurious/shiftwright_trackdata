import json
from pathlib import Path
from collections import Counter

stats = Counter()

for file in Path(
    "generated/knowledge_packs"
).glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    level = data.get(
        "knowledge_registry",
        {}
    ).get(
        "knowledge_level",
        "unknown"
    )

    stats[level] += 1

print()

for key,value in sorted(stats.items()):

    print(
        f"{key}: {value}"
    )
