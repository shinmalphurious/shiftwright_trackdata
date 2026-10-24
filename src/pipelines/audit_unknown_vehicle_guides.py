import json
from pathlib import Path

for file in Path(
    "generated/guide_catalog"
).glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    for car,videos in data.get(
        "selected_guides",
        {}
    ).items():

        if car:
            continue

        print()
        print(
            file.name
        )

        for video in videos:

            print(
                video["title"]
            )
