import json

with open(
    "registry/track_categories.json",
    encoding="utf-8"
) as fp:
    categories = json.load(fp)

with open(
    "registry/lovely_coverage.json",
    encoding="utf-8"
) as fp:
    lovely = json.load(fp)

for track_id, info in categories.items():

    if info["category"] != "Road":
        continue

    if lovely.get(
        track_id,
        {}
    ).get(
        "lovely_available",
        False
    ):
        continue

    print(
        track_id,
        info["venue"]
    )
