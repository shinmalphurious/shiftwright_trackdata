import json
from pathlib import Path

manifest_path = (
    "generated/track_acquisition_manifest.json"
)

manifest = json.load(
    open(
        manifest_path,
        encoding="utf-8"
    )
)

transcripts = {
    p.stem
    for p in Path(
        "research/youtube/transcripts"
    ).glob("*.json")
}

updated = 0

for track in manifest:

    youtube = track.get(
        "youtube",
        {}
    )

    video_ids = youtube.get(
        "video_ids",
        []
    )

    transcript_count = sum(
        1
        for video_id in video_ids
        if video_id in transcripts
    )

    track[
        "knowledge"
    ][
        "transcript_count"
    ] = transcript_count

    if transcript_count > 0:

        track[
            "knowledge"
        ][
            "transcript_acquired"
        ] = True

        if track["state"] == "videos_found":

            track["state"] = (
                "transcript_acquired"
            )

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
