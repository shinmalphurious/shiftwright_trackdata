import json
from pathlib import Path

catalog = {
    t["track_id"]: t
    for t in json.load(
        open(
            "generated/track_catalog.json",
            encoding="utf-8"
        )
    )
}

updated = 0

for file in Path(
    "generated/knowledge_packs"
).glob("*.json"):

    track_id = int(file.stem)

    pack = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    track_info = catalog.get(
        track_id,
        {}
    )

    pack["track_catalog"] = {

        "layout":
            track_info.get(
                "layout"
            ),

        "folder":
            track_info.get(
                "folder"
            ),

        "has_active_svg":
            track_info.get(
                "has_active_svg"
            ),

        "has_turns_svg":
            track_info.get(
                "has_turns_svg"
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
