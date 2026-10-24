import json
from pathlib import Path

PACK_DIR = Path(
    "generated/knowledge_packs"
)

updated = 0

for pack_file in PACK_DIR.glob(
    "*.json"
):

    pack = json.load(
        open(
            pack_file,
            encoding="utf-8"
        )
    )

    turns = pack.get(
        "turn_consensus",
        {}
    )

    corners = pack.get(
        "named_corners",
        []
    )

    for idx, corner in enumerate(
        corners,
        start=1
    ):

        turn_key = (
            f"turn_{idx}"
        )

        corner[
            "corner_knowledge"
        ] = turns.get(
            turn_key,
            {}
        )

    with open(
        pack_file,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            pack,
            fp,
            indent=2
        )

    updated += 1

print(
    "updated packs:",
    updated
)
