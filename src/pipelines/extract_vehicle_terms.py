import json
from collections import Counter

data = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

vehicles = Counter()

for video in data["videos"]:

    title = video["title"]

    vehicles[title] += 1

with open(
    "generated/discovered_vehicle_terms.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        dict(vehicles),
        fp,
        indent=2
    )

print(
        "unique titles:",
        len(vehicles)
)
