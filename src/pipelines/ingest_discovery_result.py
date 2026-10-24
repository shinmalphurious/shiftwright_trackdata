import json
import sys

if len(sys.argv) < 3:

    print(
        "usage: track_id video_id"
    )

    raise SystemExit

track_id = int(sys.argv[1])

video_id = sys.argv[2]

manifest_path = (
    "generated/track_acquisition_manifest.json"
)

manifest = json.load(
    open(
        manifest_path,
        encoding="utf-8"
    )
)

for track in manifest:

    if track["track_id"] != track_id:
        continue

    youtube = track.setdefault(
        "youtube",
        {}
    )

    youtube.setdefault(
        "videos_found",
        0
    )

    youtube.setdefault(
        "videos_processed",
        0
    )

    youtube.setdefault(
        "video_ids",
        []
    )

    if video_id not in youtube["video_ids"]:

        youtube["video_ids"].append(
            video_id
        )

    youtube["videos_found"] = len(
        youtube["video_ids"]
    )

    if youtube["videos_found"] > 0:

        track["state"] = (
            "videos_found"
        )

    break

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
    "ingested"
)
