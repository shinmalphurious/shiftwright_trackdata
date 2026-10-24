import json
from pathlib import Path

SUMMARY_FILE = Path(
    "research/youtube/track_fact_summary.txt"
)

OUTPUT_DIR = Path(
    "generated/youtube_knowledge"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TRACK_MAP = json.load(
    open(
        "research/youtube/track_map.json",
        encoding="utf-8"
    )
)

tracks = {}

content = SUMMARY_FILE.read_text(
    encoding="utf-16"
)

current_track = None

for line in content.splitlines():

    line = line.strip()

    if not line:
        continue

    if line.startswith("="):
        continue

    if "," not in line:

        current_track = line

        tracks.setdefault(
            current_track,
            {
                "track_summary": {},
                "turn_consensus": {}
            }
        )

        continue

    fact, count = line.split(",")

    tracks[current_track][
        "track_summary"
    ][fact.strip()] = int(count)

built = 0

for track_name, data in tracks.items():

    if track_name not in TRACK_MAP:
        continue

    track_id = TRACK_MAP[track_name]

    with open(
        OUTPUT_DIR /
        f"{track_id}.json",
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            {
                "track_id": track_id,
                "track_name": track_name,
                **data
            },
            fp,
            indent=2
        )

    built += 1

print(
    "youtube knowledge:",
    built
)

