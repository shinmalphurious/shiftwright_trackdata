import json
import subprocess
import sys
from pathlib import Path

from src.providers.provider_factory import get_provider

PYTHON = sys.executable

config = json.load(
    open(
        "generated/transcript_provider.json",
        encoding="utf-8"
    )
)

task = json.load(
    open(
        "generated/current_transcript_task.json",
        encoding="utf-8"
    )
)

provider = get_provider(
    config["provider"]
)

print()
print(
    "VIDEO:",
    task["video_id"]
)

print(
    "PROVIDER:",
    type(provider).__name__
)

try:

    transcript = provider.fetch(
        task["video_id"]
    )

    transcript_dir = Path(
        "research/youtube/transcripts"
    )

    transcript_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    outfile = (
        transcript_dir /
        f"{task['video_id']}.json"
    )

    with open(
        outfile,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            transcript,
            fp,
            indent=2,
            ensure_ascii=False
        )

    print(
        "SUCCESS"
    )

    print(
        "segments:",
        len(transcript)
    )

    print(
        "saved:",
        outfile
    )

    subprocess.run(
        [
            PYTHON,
            "-m",
            "src.pipelines.mark_transcript_downloaded"
        ]
    )

    subprocess.run(
        [
            PYTHON,
            "-m",
            "src.pipelines.sync_manifest_from_transcripts"
        ]
    )

except Exception as ex:

    print()
    print("FAILED")
    print()
    print(ex)

    message = str(ex).lower()

    if (
        "429" in message
        or "too many requests" in message
    ):

        print()
        print(
            "RATE_LIMIT_DETECTED"
        )

        subprocess.run(
            [
                PYTHON,
                "-m",
                "src.pipelines.record_transcript_429"
            ]
        )

    elif (
        "subtitles are disabled" in message
        or "transcriptsdisabled" in message
    ):

        print()
        print(
            "TRANSCRIPT_UNAVAILABLE"
        )

    elif (
        "video unavailable" in message
    ):

        print()
        print(
            "VIDEO_UNAVAILABLE"
        )

    else:

        print()
        print(
            "NON_RATE_LIMIT_FAILURE"
        )

    raise SystemExit(1)
