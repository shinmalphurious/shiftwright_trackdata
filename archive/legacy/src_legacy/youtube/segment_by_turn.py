import json
import re
from pathlib import Path

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

TURN_PATTERN = re.compile(
    r"turn\s+(\d+[a-z]?)",
    re.IGNORECASE
)

for file in TRANSCRIPTS.glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    current_turn = None

    for entry in data:

        text = entry["text"]

        match = TURN_PATTERN.search(
            text
        )

        if match:

            current_turn = (
                match.group(1)
            )

        if current_turn:

            print(
                f"{file.stem},"
                f"turn_{current_turn},"
                f"{text}"
            )
