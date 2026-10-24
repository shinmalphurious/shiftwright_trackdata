import json
import sys
from pathlib import Path

if len(sys.argv) != 3:

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

transcript_exists = (
    Path(
        f"research/youtube/transcripts/{video_id}.json"
    ).exists()
)

for track in manifest:

    if track["track_id"] != track_id:
        continue

    if transcript_exists:

        track[
            "knowledge"
        ][
            "transcript_acquired"
        ] = True

        track[
            "state"
        ] = "transcript_acquired"

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
    "transcript_found:",
    transcript_exists
)
