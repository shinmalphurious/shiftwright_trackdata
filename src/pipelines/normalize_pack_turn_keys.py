import json
from pathlib import Path

PACK_DIR = Path(
    "generated/knowledge_packs"
)

updated = 0

for file in PACK_DIR.glob(
    "*.json"
):

    pack = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    normalized = {}

    for key, value in pack.get(
        "turn_consensus",
        {}
    ).items():

        normalized[
            key.strip()
        ] = value

    pack[
        "turn_consensus"
    ] = normalized

    with open(
        file,
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
    "normalized packs:",
    updated
)
