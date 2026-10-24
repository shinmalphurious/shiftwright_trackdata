import json
from pathlib import Path

INPUT_DIR = Path(
    "generated/corner_intelligence"
)

OUTPUT_DIR = Path(
    "generated/corner_priority"
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

    for corner in data.get(
        "corners",
        []
    ):

        knowledge = corner.get(
            "corner_knowledge",
            {}
        )

        score = 0

        score += knowledge.get(
            "braking_zone",
            0
        )

        score += knowledge.get(
            "trail_braking",
            0
        )

        score += knowledge.get(
            "exit_focus",
            0
        )

        score += knowledge.get(
            "slippery",
            0
        )

        score += knowledge.get(
            "cambered",
            0
        )

        corner[
            "coaching_priority"
        ] = score

    data[
        "corners"
    ].sort(
        key=lambda c:
            c.get(
                "coaching_priority",
                0
            ),
        reverse=True
    )

    with open(
        OUTPUT_DIR /
        file.name,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            data,
            fp,
            indent=2
        )

    built += 1

print(
    "priority files:",
    built
)
