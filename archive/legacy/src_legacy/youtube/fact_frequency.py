import json
from pathlib import Path
from collections import Counter

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

phrases = Counter()

patterns = [
    "100 board",
    "50 board",
    "late apex",
    "double apex",
    "trail brake",
    "trail braking",
    "trail it off",
    "good exit",
    "important exit",
    "carry speed",
    "passing opportunity",
    "overtaking"
]

for file in TRANSCRIPTS.glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    text = " ".join(
        x["text"]
        for x in data
    ).lower()

    for pattern in patterns:

        if pattern in text:

            phrases[pattern] += 1

print()

for phrase,count in phrases.most_common():

    print(
        f"{phrase},{count}"
    )
