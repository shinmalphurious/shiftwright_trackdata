import json
from pathlib import Path

LOVELY_DIR = Path(
    "imports/lovely"
)

APEX_DIR = Path(
    "generated/corner_apexes"
)

total_tracks = 0

matching = 0

for lovely_file in LOVELY_DIR.glob(
    "*.json"
):

    track_id = lovely_file.stem

    apex_file = (
        APEX_DIR /
        f"{track_id}.json"
    )

    if not apex_file.exists():
        continue

    lovely = json.load(
        open(
            lovely_file,
            encoding="utf-8"
        )
    )

    apexes = json.load(
        open(
            apex_file,
            encoding="utf-8"
        )
    )

    lovely_count = len(
        lovely.get(
            "corners",
            []
        )
    )

    generated_count = apexes.get(
        "apex_count",
        0
    )

    total_tracks += 1

    if lovely_count == generated_count:

        matching += 1

    print(
        f"{track_id:>4} | "
        f"Lovely={lovely_count:>2} | "
        f"Generated={generated_count:>2}"
    )

print()
print(
    f"Tracks compared: {total_tracks}"
)

print(
    f"Exact matches: {matching}"
)

print(
    f"Match rate: "
    f"{matching/total_tracks:.1%}"
)
