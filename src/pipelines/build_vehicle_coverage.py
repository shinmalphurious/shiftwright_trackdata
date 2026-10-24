import json
from collections import Counter

registry = json.load(
    open(
        "generated/guide_registry.json",
        encoding="utf-8"
    )
)

coverage = Counter()

for row in registry:

    coverage[
        row["car"]
    ] += row[
        "guide_count"
    ]

with open(
    "generated/vehicle_coverage.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        dict(
            coverage.most_common()
        ),
        fp,
        indent=2
    )

print(
        "classes:",
        len(coverage)
)
