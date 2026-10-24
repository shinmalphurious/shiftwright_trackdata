import csv
from collections import defaultdict, Counter

THEMES = {
    "momentum_track":[
        "carry speed",
        "momentum"
    ],
    "high_speed":[
        "flat out",
        "high speed"
    ],
    "technical":[
        "technical"
    ],
    "overtaking":[
        "passing opportunity",
        "overtake",
        "overtaking"
    ],
    "off_camber":[
        "off camber"
    ],
    "cambered":[
        "camber"
    ],
    "blind_corner":[
        "blind"
    ],
    "double_apex":[
        "double apex"
    ],
    "late_apex":[
        "late apex"
    ],
    "banking":[
        "banking"
    ]
}

video_track = {}

with open(
    "research/youtube/video_metadata.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 2:
            continue

        video_track[row[0]] = row[1]

track_themes = defaultdict(Counter)

with open(
    "research/youtube/turn_ranges.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 3:
            continue

        track = video_track.get(
            row[0]
        )

        if not track:
            continue

        text = row[2].lower()

        for theme,patterns in THEMES.items():

            if any(
                p in text
                for p in patterns
            ):
                track_themes[
                    track
                ][theme] += 1

for track,themes in track_themes.items():

    print()
    print(track)

    for theme,count in themes.most_common():

        print(
            f"  {theme}: {count}"
        )
