import json

parent = json.load(
    open(
        "generated\\485.json",
        encoding="utf-8"
    )
)

regions = json.load(
    open(
        "generated\\corner_regions\\486.json",
        encoding="utf-8"
    )
)

for region in regions["corners"]:

    apex = region["apex_pct"]

    best = None
    best_distance = 999

    for corner in parent["corners"]:

        centre = (
            corner["start_pct"]
            +
            corner["end_pct"]
        ) / 2

        distance = abs(
            apex - centre
        )

        if distance < best_distance:

            best_distance = distance
            best = corner["name"]

    print(
        f"{apex:.3f} -> {best}"
    )
