import json
from pathlib import Path
import re

registry = []

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

        for video in videos:

            title = video[
                "title"
            ]

            m = re.search(
                r"(\d+\.\d+)",
                title
            )

            laptime = (
                m.group(1)
                if m
                else None
            )

            registry.append(
                {
                    "track_id":
                        track_id,

                    "car":
                        car,

                    "video_id":
                        video[
                            "video_id"
                        ],

                    "laptime":
                        laptime,

                    "title":
                        title
                }
            )

with open(
    "generated/guide_metadata_registry.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        registry,
        fp,
        indent=2
    )

print(
        "entries:",
        len(registry)
)
