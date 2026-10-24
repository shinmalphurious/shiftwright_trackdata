import csv
import json

TRACK_MAP = json.load(
    open(
        "research/youtube/track_map.json",
        encoding="utf-8"
    )
)

registry = {}

with open(
    "research/youtube/video_metadata.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 3:
            continue

        video_id = row[0]
        track_name = row[1]
        title = row[2]

        title_lower = title.lower()

        if (
            "track guide" in title_lower or
            "lap guide" in title_lower or
            "guide" in title_lower
        ):
            video_type = "lap_walkthrough"

        elif (
            "hotlap" in title_lower or
            "hot lap" in title_lower
        ):
            video_type = "hotlap"

        elif (
            "setup" in title_lower
        ):
            video_type = "setup"

        else:
            video_type = "other"

        registry[video_id] = {
            "track_name": track_name,
            "track_id": TRACK_MAP.get(
                track_name
            ),
            "title": title,
            "video_type": video_type
        }

with open(
    "generated/video_track_registry.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        registry,
        fp,
        indent=2
    )

print(
    "videos:",
    len(registry)
)

