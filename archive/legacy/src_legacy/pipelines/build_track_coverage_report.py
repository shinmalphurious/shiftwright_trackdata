import csv
import json
from pathlib import Path

GENERATED = Path("generated")

TRACK_LOOKUP = {}

for track_file in GENERATED.glob("*.json"):

    try:
        data = json.load(
            open(
                track_file,
                encoding="utf-8"
            )
        )

        track_name = data.get(
            "track_name",
            track_file.stem
        )

        corner_count = len(
            data.get(
                "corners",
                []
            )
        )

        TRACK_LOOKUP[
            track_name.lower()
        ] = corner_count

    except Exception:
        pass

YOUTUBE = {}

with open(
    "research/youtube/video_metadata.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 2:
            continue

        track = row[1]

        YOUTUBE.setdefault(
            track,
            0
        )

        YOUTUBE[track] += 1

print()
print(
    "TRACK,VIDEOS,CORNERS"
)

for track,videos in sorted(
    YOUTUBE.items()
):

    corners = TRACK_LOOKUP.get(
        track.lower(),
        0
    )

    print(
        f"{track},{videos},{corners}"
    )
