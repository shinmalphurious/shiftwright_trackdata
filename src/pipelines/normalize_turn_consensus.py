import json
from pathlib import Path

DIR = Path(
    "generated/youtube_knowledge"
)

updated = 0

for file in DIR.glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    normalized = {}

    for turn,facts in data.get(
        "turn_consensus",
        {}
    ).items():

        normalized[
            turn.strip()
        ] = facts

    data[
        "turn_consensus"
    ] = normalized

    with open(
        file,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            data,
            fp,
            indent=2
        )

    updated += 1

print(
    "normalized:",
    updated
)
