import json
import re
from pathlib import Path

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

PATTERNS = {
    "BRAKING_MARKER":
        [
            "100 board",
            "50 board",
            "lamp post",
            "marshal",
            "curb"
        ],

    "DOUBLE_APEX":
        [
            "double apex"
        ],

    "EXIT_PRIORITY":
        [
            "important exit",
            "good exit",
            "exit onto",
            "carry speed"
        ],

    "TRAIL_BRAKING":
        [
            "trail brake",
            "trail it off",
            "trail braking"
        ],

    "OVERTAKING":
        [
            "overtaking",
            "passing opportunity",
            "pass"
        ]
}

for file in TRANSCRIPTS.glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    text = " ".join(
        row["text"]
        for row in data
    ).lower()

    for category, terms in PATTERNS.items():

        for term in terms:

            count = text.count(
                term
            )

            if count:

                print(
                    f"{file.stem},"
                    f"{category},"
                    f"{term},"
                    f"{count}"
                )
