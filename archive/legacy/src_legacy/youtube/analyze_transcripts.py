import json
from pathlib import Path
from collections import Counter
import re

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

keywords = [
    "brake",
    "braking",
    "turn",
    "corner",
    "apex",
    "exit",
    "entry",
    "traction",
    "kerb",
    "curb",
    "overtake",
    "overtaking",
    "straight"
]

counts = Counter()

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

    for word in keywords:

        counts[word] += len(
            re.findall(
                rf"\b{word}\b",
                text
            )
        )

print()

for k,v in counts.most_common():

    print(
        f"{k},{v}"
    )
