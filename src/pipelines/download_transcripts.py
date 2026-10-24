import json
import subprocess
import sys

task = next(
    (
        t for t in json.load(
            open(
                "generated/transcript_tasks.json",
                encoding="utf-8"
            )
        )
        if not t.get(
            "transcript_exists",
            False
        )
    ),
    None
)

if not task:

    print(
        "no transcript work"
    )

    raise SystemExit

video_id = task[
    "video_id"
]

track_id = task[
    "track_id"
]

print(
    "attempting",
    video_id
)

try:

    from youtube_transcript_api import (
        YouTubeTranscriptApi
    )

    transcript = (
        YouTubeTranscriptApi()
        .fetch(video_id)
    )

    print(
        "transcript success"
    )

except Exception as ex:

    print(
        "transcript failed"
    )

    print(ex)

    subprocess.run(
        [ sys.executable,
            "-m",
            "src.pipelines.schedule_transcript_retry",
            str(track_id)
        ]
    )

    raise SystemExit

print(
    "completed"
)

