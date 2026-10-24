import json
from pathlib import Path
from collections import defaultdict, Counter
import csv

TRACK_MAP = {
    "Road Atlanta": {
        "id": 127,
        "folder": r"external\racing-track-maps-vector\from-iracing\Road\roadatlanta\127-roadatlanta-full"
    },
    "Bathurst": {
        "id": 219,
        "folder": r"external\racing-track-maps-vector\from-iracing\Road\bathurst\219-bathurst"
    },
    "Zandvoort": {
        "id": 485,
        "folder": r"external\racing-track-maps-vector\from-iracing\Road\zandvoort\485-zandvoort-2023-gp"
    },
    "Spa": {
        "id": 525,
        "folder": r"external\racing-track-maps-vector\from-iracing\Road\spa\525-spa-2024-combined"
    }
}

video_track = {}

with open(
    "research/youtube/video_metadata.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) >= 2:
            video_track[row[0]] = row[1]

track_summary = defaultdict(Counter)
corner_summary = defaultdict(lambda: defaultdict(Counter))

with open(
    "research/youtube/turn_facts_v2.csv",
    encoding="utf-16"
) as f:

    for line in f:

        line = line.strip()

        if ":" not in line:
            continue

        left,right = line.split(",",1)

        video_id,turn = left.split(":",1)

        track = video_track.get(video_id)

        if not track:
            continue

        for fact in right.split(","):

            fact = fact.strip()

            if not fact:
                continue

            track_summary[track][fact] += 1
            corner_summary[track][turn][fact] += 1

for track_name,data in TRACK_MAP.items():

    output = {
        "track_name": track_name,
        "track_id": data["id"],
        "track_summary": dict(
            track_summary[track_name]
        ),
        "corner_consensus": {
            turn: dict(facts)
            for turn,facts
            in corner_summary[track_name].items()
        }
    }

    out_file = (
        Path(data["folder"])
        / "commentary.json"
    )

    out_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        out_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print(
        "wrote",
        out_file
    )
