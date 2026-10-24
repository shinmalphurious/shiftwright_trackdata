import json
from collections import defaultdict

data = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

cars = defaultdict(list)

for video in data["videos"]:

    car = video.get(
        "car"
    )

    if not car:
        continue

    score = 0

    if (
        video["video_type"]
        ==
        "lap_walkthrough"
    ):
        score += 100

    title = video[
        "title"
    ].lower()

    if "iracing" in title:
        score += 50

    cars[car].append(
        (
            score,
            video
        )
    )

selected = {}

for car,videos in cars.items():

    videos.sort(
        key=lambda x: x[0],
        reverse=True
    )

    selected[car] = [
        video
        for score,video
        in videos[:3]
    ]

result = {
    "track_id":
        data["track_id"],

    "layout":
        data["layout"],

    "selected_guides":
        selected
}

with open(
    "generated/discovery_selection.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        result,
        fp,
        indent=2
    )

print(
        "cars:",
        len(selected)
)
