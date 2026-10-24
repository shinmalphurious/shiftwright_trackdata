import json
from collections import defaultdict

data = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

groups = defaultdict(list)

for video in data["videos"]:

    car = (
        video["car"]
        if video["car"]
        else "unknown"
    )

    groups[car].append(
        video
    )

output = {
    "track_id":
        data["track_id"],

    "layout":
        data["layout"],

    "cars": dict(groups)
}

with open(
    "generated/discovery_groups.json",
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
        len(groups)
)
