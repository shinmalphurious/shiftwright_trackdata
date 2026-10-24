import json
from collections import defaultdict

track_catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

mapping = defaultdict(list)

for track in track_catalog:

    layout = track["layout"]

    track_id = track["track_id"]

    parts = layout.split("-")

    if len(parts) < 2:
        continue

    venue = (
        parts[1]
        .replace("_"," ")
        .title()
    )

    mapping[
        venue
    ].append(
        track_id
    )

with open(
    "research/youtube/track_map.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        dict(mapping),
        fp,
        indent=2
    )

print(
        "venues:",
        len(mapping)
)
