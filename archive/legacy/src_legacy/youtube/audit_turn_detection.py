import json
import re
from pathlib import Path

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

NUMBER_WORDS = (
    "one|two|three|four|five|six|seven|eight|nine|ten|"
    "eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
    "seventeen|eighteen"
)

TURN_RE = re.compile(
    rf"turn\s+(\d+[a-z]?|{NUMBER_WORDS})",
    re.I
)

for file in TRANSCRIPTS.glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    count = 0

    for row in data:

        if TURN_RE.search(
            row["text"]
        ):
            count += 1

    if count:

        print(
            f"{file.stem},{count}"
        )
