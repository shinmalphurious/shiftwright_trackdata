import json
from pathlib import Path

SOURCE_DIR = Path(
    "generated/youtube_knowledge"
)

OUTPUT_DIR = Path(
    "generated/youtube_confidence"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for file in SOURCE_DIR.glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    confidence = {}

    for turn, facts in data.get(
        "turn_consensus",
        {}
    ).items():

        total = sum(
            facts.values()
        )

        turn_scores = {}

        for fact,count in facts.items():

            score = round(
                count / total,
                3
            )

            turn_scores[
                fact
            ] = score

        confidence[
            turn
        ] = turn_scores

    with open(
        OUTPUT_DIR /
        file.name,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            confidence,
            fp,
            indent=2
        )

    built += 1

print(
    "confidence files:",
    built
)
