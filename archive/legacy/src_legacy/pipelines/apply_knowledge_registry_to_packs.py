import json
from pathlib import Path

registry = {
    r["track_id"]: r
    for r in json.load(
        open(
            "generated/knowledge_registry.json",
            encoding="utf-8"
        )
    )
}

updated = 0

for file in Path(
    "generated/knowledge_packs"
).glob("*.json"):

    track_id = int(
        file.stem
    )

    pack = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    record = registry.get(
        track_id,
        {}
    )

    pack["knowledge_registry"] = {

        "knowledge_level":
            record.get(
                "knowledge_level",
                "unknown"
            ),

        "named_corner_count":
            record.get(
                "named_corner_count",
                0
            ),

        "generated_corner_count":
            record.get(
                "generated_corner_count",
                0
            ),

        "parent_track_id":
            record.get(
                "parent_track_id"
            ),

        "inheritance_level":
            record.get(
                "inheritance_level"
            )
    }

    with open(
        file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            pack,
            f,
            indent=2
        )

    updated += 1

print(
    "updated",
    updated,
    "knowledge packs"
)
