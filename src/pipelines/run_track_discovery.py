import subprocess
import sys

PYTHON = sys.executable

steps = [

    "claim_next_track",

    "build_search_payload",

    "build_discovery_task",

    "run_discovery_provider",

    "select_best_guides",

    "store_selected_guides",

    "archive_discovery_selection",

    "archive_discovery_selection"

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
        ]
    )

    if result.returncode != 0:

        print()
        print(
            "FAILED:",
            step
        )

        raise SystemExit

print()
print(
    "TRACK_GUIDES_CATALOGUED"
)


