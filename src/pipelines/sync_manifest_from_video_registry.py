import json
from collections import Counter

manifest_path = (
    "generated/track_acquisition_manifest.json"
)

registry = json.load(
    open(
        "generated/video_track_registry.json",
        encoding="utf-8"
    )
)

manifest = json.load(
    open(
        manifest_path,
        encoding="utf-8"
    )
)

counts = Counter()
video_ids = {}

for video in registry.values():

    track_id = video.get(
        "track_id"
    )

    if track_id:
        counts[track_id] += 1

        if track_id not in video_ids:
            video_ids[track_id] = []

        video_ids[track_id].append(
            video_ids
        )

updated = 0

for track in manifest:

    track_id = track[
        "track_id"
    ]

    found = counts.get(
        track_id,
        0
    )

    track[
        "youtube"
    ][
        "videos_found"
    ] = found

    track[
        "youtube"
    ][
        "video_ids"
    ] = video_ids.get(
        track_id,
        []
    )

    if (
        found > 0
        and
        track["state"] == "pending_search"
    ):

        track["state"] = "videos_found"

    updated += 1

with open(
    manifest_path,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        manifest,
        fp,
        indent=2
    )

print(
    "tracks updated:",
    updated
)

