import json
import re
from pathlib import Path
from collections import Counter

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

counter = Counter()

patterns = [
    r"turn\s+\d+[a-z]?",
    r"\b[a-z]+\s+corner\b",
    r"\b[a-z]+\s+bend\b",
    r"\b[a-z]+\s+stop\b",
    r"\b[a-z]+\s+source\b",
    r"\b[a-z]+\s+rouge\b",
    r"\b[a-z]+\s+combes\b"
]

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

    for pattern in patterns:

        for match in re.findall(
            pattern,
            text
        ):

            counter[match] += 1

for name,count in counter.most_common():

    if count >= 2:

        print(
            f"{name},{count}"
        )
