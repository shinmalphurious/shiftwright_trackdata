import json

result = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

manifest_path = (
    "generated/track_acquisition_manifest.json"
)

manifest = json.load(
    open(
        manifest_path,
        encoding="utf-8"
    )
)

track_id = result["track_id"]

videos = result.get(
    "videos",
    []
)

for track in manifest:

    if track["track_id"] != track_id:
        continue

    youtube = track.setdefault(
        "youtube",
        {}
    )

    youtube.setdefault(
        "video_ids",
        []
    )

    for video in videos:

        video_id = video.get(
            "video_id"
        )

        if (
            video_id
            and
            video_id not in youtube["video_ids"]
        ):

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
    "videos ingested:",
    len(videos)
)
