import csv
import json
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi

ROOT = Path.cwd()

INPUT = (
    ROOT /
    "research" /
    "youtube" /
    "catalog" /
    "discovered_videos.csv"
)

OUTPUT = (
    ROOT /
    "research" /
    "youtube" /
    "transcripts"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)

api = YouTubeTranscriptApi()

success = 0
failed = 0

with open(
    INPUT,
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        video_id = row["video_id"]

        outfile = (
            OUTPUT /
            f"{video_id}.json"
        )

        if outfile.exists():
            continue

        try:

            transcript = api.fetch(
                video_id
            )

            with open(
                outfile,
                "w",
                encoding="utf-8"
            ) as out:

                json.dump(
                    transcript.to_raw_data(),
                    out,
                    indent=2
                )

            success += 1

            print(
                f"OK {video_id}"
            )

        except Exception:

            failed += 1

            print(
                f"FAIL {video_id}"
            )

print()
print(
    f"success={success}"
)
print(
    f"failed={failed}"
)
