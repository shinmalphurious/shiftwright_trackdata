import json
from collections import defaultdict

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

stats = defaultdict(
    lambda:{
        "total":0,
        "lovely":0
    }
)

for track_id, record in categories.items():

    category = record["category"]

    stats[category]["total"] += 1

    if lovely.get(
        track_id,
        {}
    ).get(
        "lovely_available",
        False
    ):
        stats[category]["lovely"] += 1

print()

for category, values in sorted(
    stats.items()
):

    pct = (
        values["lovely"]
        / values["total"]
        * 100
    )

    print(
        f"{category:<12} "
        f"{values['lovely']:>4}/"
        f"{values['total']:<4} "
        f"{pct:>5.1f}%"
    )
