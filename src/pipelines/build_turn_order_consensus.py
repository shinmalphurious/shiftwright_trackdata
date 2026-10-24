import json
from collections import defaultdict

video_registry = json.load(
    open(
        "generated/video_track_registry.json",
        encoding="utf-8"
    )
)

turn_order = json.load(
    open(
        "generated/turn_order_library.json",
        encoding="utf-8"
    )
)

track_orders = defaultdict(list)

for video_id, order_data in turn_order.items():

    meta = video_registry.get(
        video_id
    )

    if not meta:
        continue

    track_id = meta.get(
        "track_id"
    )

    if not track_id:
        continue

    track_orders[
        str(track_id)
    ].append(
        order_data["turn_order"]
    )

with open(
    "generated/turn_order_consensus.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        track_orders,
        fp,
        indent=2
    )

print(
    "tracks:",
    len(track_orders)
)
