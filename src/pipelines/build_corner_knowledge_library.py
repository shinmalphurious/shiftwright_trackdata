import json
from pathlib import Path

PACK_DIR = Path(
    "generated/knowledge_packs"
)

OUTPUT_DIR = Path(
    "generated/corner_knowledge"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

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

    corners = []

    for idx, corner in enumerate(
        pack.get(
            "named_corners",
            []
        ),
        start=1
    ):

        turn_key = f"turn_{idx}"

        enriched = dict(
            corner
        )

        enriched[
            "corner_knowledge"
        ] = turns.get(
            turn_key,
            {}
        )

        corners.append(
            enriched
        )

    with open(
        OUTPUT_DIR /
        pack_file.name,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            {
                "track_id":
                    pack["track_id"],
                "corners":
                    corners
            },
            fp,
            indent=2
        )

    built += 1

print(
    "corner knowledge:",
    built
)
