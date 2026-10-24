import json

registry = json.load(
    open(
        "generated/guide_registry.json",
        encoding="utf-8"
    )
)

tracks = set()

cars = set()

guides = 0

for entry in registry:

    tracks.add(
        entry["track_id"]
    )

    cars.add(
        entry["car"]
    )

    guides += (
        entry["guide_count"]
    )

print()

print(
    "tracks:",
    len(tracks)
)

print(
    "cars:",
    len(cars)
)

print(
    "guides:",
    guides
)
