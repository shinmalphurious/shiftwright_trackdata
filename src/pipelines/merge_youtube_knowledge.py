import json
from pathlib import Path

knowledge_dir = Path(
    "generated/youtube_knowledge"
)

consensus_dir = Path(
    "generated/turn_consensus"
)

updated = 0

for knowledge_file in knowledge_dir.glob(
    "*.json"
):

    track_id = knowledge_file.stem

    consensus_file = (
        consensus_dir /
        f"{track_id}.json"
    )

    if not consensus_file.exists():
        continue

    knowledge = json.load(
        open(
            knowledge_file,
            encoding="utf-8"
        )
    )

    consensus = json.load(
        open(
            consensus_file,
            encoding="utf-8"
        )
    )

    knowledge[
        "turn_consensus"
    ] = consensus

    with open(
        knowledge_file,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            knowledge,
            fp,
            indent=2
        )

    updated += 1

print(
    "updated:",
    updated
)
