import csv
import json
from pathlib import Path

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

with open(
    "research/youtube/video_metadata.csv",
    encoding="utf-16"
) as f:


    rows = list(
        csv.reader(f)
    )

video_map = {}

for row in rows:

    if len(row) < 3:
        continue

    video_map[row[0]] = {
        "track": row[1],
        "title": row[2]
    }

for file in TRANSCRIPTS.glob("*.json"):

    vid = file.stem

    if vid not in video_map:
        continue

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    word_count = sum(
        len(
            x["text"].split()
        )
        for x in data
    )

    print(
        f"{vid},"
        f"{video_map[vid]['track']},"
        f"{word_count}"
    )
