import json
from pathlib import Path

INPUT_DIR = Path(
    "generated/youtube_knowledge"
)

OUTPUT_DIR = Path(
    "generated/corner_attention"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for file in INPUT_DIR.glob(
    "*.json"
):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    attention = {}

    for turn, facts in data.get(
        "turn_consensus",
        {}
    ).items():

        attention[
            turn
        ] = sum(
            facts.values()
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
                    data["track_id"],
                "track_name":
                    data["track_name"],
                "attention":
                    attention
            },
            fp,
            indent=2
        )

    built += 1

print(
    "attention models:",
    built
)
