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

results = []

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

    used.add(best_idx)

    if best_distance <= 0.03:
        confidence = "high"
    elif best_distance <= 0.06:
        confidence = "medium"
    else:
        confidence = "low"

    results.append(
        {
            "name":
                parent["corners"][best_idx]["name"],
            "apex_pct":
                apex,
            "distance":
                round(best_distance,4),
            "confidence":
                confidence
        }
    )

print(
    json.dumps(
        results,
        indent=2
    )
)
