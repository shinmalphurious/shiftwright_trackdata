import json
from pathlib import Path

report = []

for file in Path(
    "generated/guide_catalog"
).glob(
    "*.json"
):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    car_count = len(
        data.get(
            "selected_guides",
            {}
        )
    )

    guide_count = sum(
        len(v)
        for v in data.get(
            "selected_guides",
            {}
        ).values()
    )

    report.append(
        {
            "track_id":
                data["track_id"],

            "layout":
                data["layout"],

            "cars":
                car_count,

            "guides":
                guide_count
        }
    )

report.sort(
    key=lambda x:
        x["cars"],
    reverse=True
)

with open(
    "generated/discovery_effectiveness.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        report,
        fp,
        indent=2
    )

print(
    "tracks:",
    len(report)
)
