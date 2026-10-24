import csv
import json

registry = json.load(
    open(
        "generated/video_track_registry.json",
        encoding="utf-8"
    )
)

turns = json.load(
    open(
        "generated/turn_order_library.json",
        encoding="utf-8"
    )
)

missing = []

for video_id in registry:

    if video_id not in turns:

        missing.append(
            registry[video_id]
        )

with open(
    "generated/missing_turn_order_videos.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        missing,
        fp,
        indent=2
    )

print(
    "missing:",
    len(missing)
)
