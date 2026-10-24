import json
import re
from pathlib import Path

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

KEYWORDS = [
    "brake",
    "braking",
    "apex",
    "entry",
    "exit",
    "corner",
    "curb",
    "straight"
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
    )

    sentences = re.split(
        r"[.!?]",
        text
    )

    for sentence in sentences:

        lower = sentence.lower()

        if any(
            word in lower
            for word in KEYWORDS
        ):

            if len(
                sentence.strip()
            ) > 30:

                print(
                    file.stem,
                    "|",
                    sentence.strip()
                )
