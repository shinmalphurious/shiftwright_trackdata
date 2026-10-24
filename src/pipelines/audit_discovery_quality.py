import json

results = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

lap = 0
other = 0

cars = set()

for video in results["videos"]:

    if video["video_type"] == "lap_walkthrough":
        lap += 1
    else:
        other += 1

    if video["car"]:
        cars.add(
            video["car"]
        )

print()

print(
    "lap_walkthrough:",
    lap
)

print(
    "other:",
    other
)

print(
    "cars:",
    len(cars)
)

print(
    sorted(cars)
)
