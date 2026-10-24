import json
import re
from pathlib import Path
from collections import Counter

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

patterns = [
    r"(?:turn\s+\d+[a-z]?)",
    r"(?:[a-z]+\s+corner)",
    r"(?:[a-z]+\s+bend)",
]

counter = Counter()

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

for item,count in counter.most_common():

    if count >= 2:

        print(
            f"{item},{count}"
        )
