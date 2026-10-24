import json
from pathlib import Path

guide_dir = Path(
    "generated/guide_catalog"
)

tracks = 0
cars = set()
guides = 0

for file in guide_dir.glob("*.json"):

    tracks += 1

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    for car,videos in data.get(
        "selected_guides",
        {}
    ).items():

        cars.add(car)

        guides += len(videos)

print()

print(
    "tracks:",
    tracks
)

print(
    "cars:",
    len(cars)
)

print(
    "guides:",
    guides
)

print()

for car in sorted(cars):

    print(car)
