import subprocess
import sys

PYTHON = sys.executable

steps = [
    "release_transcript_queue",
    "claim_next_transcript",
    "attempt_transcript_download"
]

for step in steps:

    print()
    print("=" * 60)
    print(step)
    print("=" * 60)

    result = subprocess.run(
        [
            PYTHON,
            "-m",
            f"src.pipelines.{step}"
        ],
        capture_output=True,
        text=True
    )

    print(
        result.stdout
    )

    if (
        "GLOBAL_TRANSCRIPT_PAUSE"
        in result.stdout
    ):
        print(
            "PIPELINE PAUSED"
        )
        break

    if result.returncode:
        break
