import json
import sys
from datetime import datetime, timedelta

track_id = int(
    sys.argv[1]
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

for track in manifest:

    if track["track_id"] != track_id:
        continue

    knowledge = track[
        "knowledge"
    ]

    attempts = (
        knowledge.get(
            "transcript_attempts",
            0
        ) + 1
    )

    knowledge[
        "transcript_attempts"
    ] = attempts

    cooldown = min(
        attempts * 30,
        1440
    )

    knowledge[
        "next_transcript_try"
    ] = (
        datetime.now().astimezone()
        +
        timedelta(
            minutes=cooldown
        )
    ).isoformat()

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
    "cooldown scheduled"
)

