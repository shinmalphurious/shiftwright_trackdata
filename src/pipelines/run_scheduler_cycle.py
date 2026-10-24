import subprocess
import sys

PYTHON = sys.executable

print()
print(
    "RUNNING DISCOVERY CYCLE"
)
print()

subprocess.run(
    [
        PYTHON,
        "-m",
        "src.pipelines.run_track_discovery"
    ]
)

print()
print(
    "RUNNING TRANSCRIPT CHECK"
)
print()

subprocess.run(
    [
        PYTHON,
        "-m",
        "src.pipelines.claim_next_transcript_task"
    ]
)

print()
print(
    "CYCLE COMPLETE"
)
