import random
import subprocess
import sys
import time
from datetime import datetime

PYTHON = sys.executable

successes = 0
failures = 0

while True:

    print()
    print("=" * 80)
    print(datetime.now().isoformat())
    print("=" * 80)

    result = subprocess.run(
        [
            PYTHON,
            "-m",
            "src.pipelines.run_transcript_pipeline"
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout

    print(output)

    with open(
        "generated/transcript_master.log",
        "a",
        encoding="utf-8"
    ) as fp:

        fp.write(
            "\n"
            + "=" * 80
            + "\n"
            + datetime.now().isoformat()
            + "\n"
            + output
            + "\n"
        )

    lower = output.lower()

    if (
        "global_transcript_pause" in lower
        or "rate_limit_detected" in lower
        or "blocking requests from your ip" in lower
    ):

        print()
        print("RATE LIMIT DETECTED")
        print("STOPPING MASTER PIPELINE")

        break

    if "success" in lower:
        successes += 1

    if "failed" in lower:
        failures += 1

    print()
    print("successes:", successes)
    print("failures:", failures)

    wait_seconds = random.randint(
        30,
        120
    )

    print()
    print(
        "sleeping",
        wait_seconds,
        "seconds"
    )

    time.sleep(
        wait_seconds
    )
