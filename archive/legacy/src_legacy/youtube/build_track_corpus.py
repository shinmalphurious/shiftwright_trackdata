import csv
import json
from pathlib import Path

TRANSCRIPTS = Path(
    "research/youtube/transcripts"
)

video_to_track = {}

with open(
    "research/youtube/video_metadata.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 2:
            continue

        video_to_track[row[0]] = row[1]

tracks = {}

for file in TRANSCRIPTS.glob("*.json"):

    vid = file.stem

    if vid not in video_to_track:
        continue

    track = video_to_track[vid]

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

    tracks.setdefault(
        track,
        []
    ).append(text)

OUTPUT = Path(
    "research/youtube/track_corpus"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)

for track,texts in tracks.items():

    with open(
        OUTPUT / f"{track}.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n\n".join(texts)
        )

print(
    f"built {len(tracks)} corpora"
)
