import csv
from collections import defaultdict, Counter

signals = {
    "slippery": [
        "slippery",
        "slippy"
    ],
    "trail_brake": [
        "trail brake",
        "trail braking",
        "trail it off"
    ],
    "cambered": [
        "cambered",
        "camber"
    ],
    "early_throttle": [
        "back on the gas",
        "pick back up on the gas",
        "100% at the apex",
        "100% before the apex"
    ]
}

track_counts = defaultdict(Counter)

with open(
    "research/youtube/turn_ranges.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 3:
            continue

        video_id = row[0]
        turn = row[1]
        text = row[2].lower()

        # crude track recovery from video id prefix file
        if "spa" in text:
            track = "Spa"
        elif "zandvoort" in text:
            track = "Zandvoort"
        elif "bathurst" in text:
            track = "Bathurst"
        elif "atlanta" in text:
            track = "Road Atlanta"
        else:
            track = "Unknown"

        for signal, phrases in signals.items():

            if any(
                p in text
                for p in phrases
            ):
                track_counts[track][signal] += 1

for track in sorted(track_counts):

    print()
    print(track)

    for signal,count in track_counts[track].most_common():

        print(
            f"  {signal}: {count}"
        )
