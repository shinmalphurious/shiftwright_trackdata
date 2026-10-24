import json
from collections import Counter

data = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

cars = Counter()

for video in data["videos"]:

    car = video.get(
        "car"
    )

    if car:

        cars[car] += 1

output = {
    "track_id":
        data["track_id"],

    "layout":
        data["layout"],

    "cars":
        dict(cars)
}

with open(
    "generated/car_profile.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        output,
        fp,
        indent=2
    )

print(
        "cars:",
        len(cars)
)
