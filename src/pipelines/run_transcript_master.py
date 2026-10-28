"""Loop run_transcript_pipeline with a random pause between cycles.

Stops on a rate limit, a global pause, or when the queue is empty. Counts only new
transcripts as successes.
"""
import random
import subprocess
import sys
import time
from datetime import datetime

PYTHON = sys.executable
LOG = "generated/transcript_master.log"

successes = failures = unavailable = 0

while True:
    stamp = datetime.now().isoformat()
    print()
    print("=" * 80)
    print(stamp)
    print("=" * 80)

    # Pick up guides that run_guide_discovery found since the last cycle
    subprocess.run([PYTHON, "-m", "src.pipelines.build_transcript_queue"])
    result = subprocess.run([PYTHON, "-m", "src.pipelines.run_transcript_pipeline"],
                            capture_output=True, text=True)
    output = result.stdout
    print(output)
    with open(LOG, "a", encoding="utf-8") as fp:
        fp.write("\n" + "=" * 80 + "\n" + stamp + "\n" + output + "\n")

    if "RATE_LIMIT_DETECTED" in output or "GLOBAL_TRANSCRIPT_PAUSE" in output:
        print("\nRATE LIMIT - STOPPING MASTER PIPELINE")
        break
    if "QUEUE_EMPTY" in output:
        print("\nQUEUE EMPTY - NOTHING LEFT TO DOWNLOAD\n")
        subprocess.run([PYTHON, "-m", "src.pipelines.sync_manifest_from_transcripts"])
        subprocess.run([PYTHON, "-m", "src.pipelines.verify_lap_guide_transcripts"])
        break

    if "NEW_TRANSCRIPT" in output:
        successes += 1
    elif "TRANSCRIPT_UNAVAILABLE" in output:
        unavailable += 1
    elif "FAILED" in output or "NO_TASK" in output:
        failures += 1

    print("\nnew transcripts:", successes, " unavailable:", unavailable, " failures:", failures)
    wait_seconds = random.randint(30, 120)
    print("\nsleeping", wait_seconds, "seconds")
    time.sleep(wait_seconds)
