"""One cycle: release due items, claim the next video, download its transcript."""
import subprocess
import sys

PYTHON = sys.executable

STEPS = ["release_transcript_queue", "claim_next_transcript", "attempt_transcript_download"]

for step in STEPS:
    print()
    print("=" * 60)
    print(step)
    print("=" * 60)
    result = subprocess.run([PYTHON, "-m", f"src.pipelines.{step}"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr.strip():
        print(result.stderr.strip().splitlines()[-1])
    if "GLOBAL_TRANSCRIPT_PAUSE" in result.stdout:
        print("PIPELINE PAUSED")
        break
    if "QUEUE_EMPTY" in result.stdout:
        break
    if result.returncode:
        break
