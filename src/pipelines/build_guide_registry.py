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

    track_id = data[
        "track_id"
    ]

    for car,videos in data[
        "selected_guides"
    ].items():

        catalog.append(
            {
                "track_id":
                    track_id,

                "car":
                    car,

                "guide_count":
                    len(videos)
            }
        )

with open(
    "generated/guide_registry.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        catalog,
        fp,
        indent=2
    )

print(
    "entries:",
    len(catalog)
)
