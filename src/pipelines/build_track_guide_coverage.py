import json
from pathlib import Path

catalog = []

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

    cars = []

    for car,videos in data.get(
        "selected_guides",
        {}
    ).items():

        cars.append(
            {
                "car": car,
                "guides": len(videos)
            }
        )

    catalog.append(
        {
            "track_id":
                data["track_id"],

            "layout":
                data["layout"],

            "cars":
                cars
        }
    )

with open(
    "generated/track_guide_coverage.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        catalog,
        fp,
        indent=2
    )

print(
        "tracks:",
        len(catalog)
)
