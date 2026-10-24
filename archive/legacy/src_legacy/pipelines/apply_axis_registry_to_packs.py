import json
from pathlib import Path

axis = json.load(
    open(
        "generated/axis_registry.json",
        encoding="utf-8"
    )
)

updated = 0

for file in Path(
    "generated/knowledge_packs"
).glob("*.json"):

    track_id = file.stem

    pack = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    pack["axis"] = axis.get(
        track_id,
        {}
    )

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
    "packs"
)
