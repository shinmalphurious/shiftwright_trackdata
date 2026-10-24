import json
import re
from pathlib import Path

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

NUMBER_WORDS = {
    "one":"1",
    "two":"2",
    "three":"3",
    "four":"4",
    "five":"5",
    "six":"6",
    "seven":"7",
    "eight":"8",
    "nine":"9",
    "ten":"10",
    "eleven":"11",
    "twelve":"12",
    "thirteen":"13",
    "fourteen":"14",
    "fifteen":"15",
    "sixteen":"16",
    "seventeen":"17",
    "eighteen":"18"
}

count = 0

for file in TRANSCRIPTS.glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    for row in data:

        text = row["text"].lower()

        if re.search(
            r"turn\s+\d+",
            text
        ):
            count += 1

        for word in NUMBER_WORDS:

            if f"turn {word}" in text:

                count += 1

print(
    "turn references:",
    count
)
