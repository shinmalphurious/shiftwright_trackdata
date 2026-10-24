import json

parent = json.load(
    open(
        "generated\\501.json",
        encoding="utf-8"
    )
)

regions = json.load(
    open(
        "generated\\corner_regions\\503.json",
        encoding="utf-8"
    )
)

used = set()

for region in regions["corners"]:

    apex = region["apex_pct"]

    best_idx = None
    best_distance = 999

    for idx, corner in enumerate(
        parent["corners"]
    ):

        if idx in used:
            continue

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
            best_idx = idx

    if best_idx is not None:

        used.add(best_idx)

        print(
            f"{apex:.3f} -> "
            f"{parent['corners'][best_idx]['name']}"
        )
