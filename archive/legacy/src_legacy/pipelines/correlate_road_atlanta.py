import json
import csv
import re

registry = json.load(
    open(
        "generated/corner_research_registry.json",
        encoding="utf-8"
    )
)

road_atlanta = registry["127"]

corner_lookup = {}

for corner in road_atlanta["corners"]:

    name = corner["corner_name"]

    m = re.search(
        r"turn\s*(\d+[a-z]?)",
        name,
        re.I
    )

    if m:

        key = (
            "turn_" +
            m.group(1).lower()
        )

        corner_lookup[key] = corner

with open(
    "research/youtube/turn_facts.csv",
    encoding="utf-16"
) as f:

    for line in f:

        line = line.strip()

        if ":" not in line:
            continue

        left,right = line.split(
            ",",
            1
        )

        _,turn = left.split(
            ":",
            1
        )

        if turn not in corner_lookup:
            continue

        corner = corner_lookup[turn]

        facts = [
            x.strip()
            for x in right.split(",")
            if x.strip()
        ]

        corner["youtube_mentions"] += 1

        corner["youtube_turns"].append(
            turn
        )

        for fact in facts:

            if (
                fact
                not in corner[
                    "youtube_facts"
                ]
            ):
                corner[
                    "youtube_facts"
                ].append(
                    fact
                )

with open(
    "generated/road_atlanta_correlated.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        road_atlanta,
        f,
        indent=2
    )

print("complete")
