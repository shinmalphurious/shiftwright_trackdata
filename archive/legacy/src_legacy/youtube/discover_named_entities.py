import re
from pathlib import Path
from collections import Counter

CORPUS = Path(
    "research/youtube/track_corpus"
)

for file in CORPUS.glob("*.txt"):

    text = file.read_text(
        encoding="utf-8"
    )

    matches = re.findall(
        r"\b[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){0,2}\b",
        text
    )

    counts = Counter(matches)

    print()
    print("=" * 50)
    print(file.stem)
    print("=" * 50)

    for name,count in counts.most_common(50):

        if count >= 2:

            print(
                f"{name},{count}"
            )
