import json
import subprocess
import sys

PYTHON = sys.executable

while True:

    result = subprocess.run(
        [
            PYTHON,
            "-m",
            "src.pipelines.claim_next_track"
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()

    if (
        "no pending tracks"
        in output.lower()
    ):
        print(
            "ACQUISITION_COMPLETE"
        )
        break

    print()
    print(
        "DISCOVERING NEXT TRACK"
    )

    subprocess.run(
        [
            PYTHON,
            "-m",
            "src.pipelines.run_track_discovery"
        ]
    )
