import subprocess
import sys

PYTHON = sys.executable

LIMIT = 25

for i in range(LIMIT):

    print()
    print(
        f"DISCOVERY {i+1}/{LIMIT}"
    )

    result = subprocess.run(
        [
            PYTHON,
            "-m",
            "src.pipelines.run_track_discovery"
        ]
    )

    if result.returncode != 0:

        print(
            "STOPPED"
        )

        break

print()
print(
    "BATCH COMPLETE"
)
