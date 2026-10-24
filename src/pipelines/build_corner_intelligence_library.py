import json
from pathlib import Path

PACK_DIR = Path(
    "generated/knowledge_packs"
)

OUTPUT_DIR = Path(
    "generated/corner_intelligence"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for file in PACK_DIR.glob(
    "*.json"
):

    pack = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    corners = []

    for corner in pack.get(
        "named_corners",
        []
    ):

        intelligence = {
            "name":
                corner.get(
                    "name"
                ),

            "corner_knowledge":
                corner.get(
                    "corner_knowledge",
                    {}
                ),

            "start_pct":
                corner.get(
                    "start_pct"
                ),

            "end_pct":
                corner.get(
                    "end_pct"
                )
        }

        corners.append(
            intelligence
        )

    with open(
        OUTPUT_DIR /
        file.name,
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
    "corner intelligence:",
    built
)
