import csv
import json
from collections import defaultdict, Counter
from pathlib import Path

TRACK_MAP = json.load(
    open(
        "research/youtube/track_map.json",
        encoding="utf-8"
    )
)

video_track = {}

with open(
    "research/youtube/video_metadata.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 2:
            continue

        video_track[row[0]] = row[1]

track_turns = defaultdict(
    lambda: defaultdict(Counter)
)

with open(
    "research/youtube/turn_facts_v2.csv",
    encoding="utf-16"
) as f:

    for line in f:

        if ":" not in line:
            continue

        left,right = line.strip().split(
            ",",
            1
        )

        video_id,turn = left.split(
            ":",
            1
        )

        track_name = video_track.get(
            video_id
        )

        if not track_name:
            continue

        if track_name not in TRACK_MAP:
            continue

        track_id = TRACK_MAP[track_name]

        for fact in right.split(","):

            fact = fact.strip()

            if fact:
                track_turns[
                    track_id
                ][turn][fact] += 1

output_dir = Path(
    "generated/turn_consensus"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for track_id, turns in track_turns.items():

    output = {}

    for turn, facts in turns.items():

        output[turn] = dict(
            facts.most_common()
        )

    with open(
        output_dir /
        f"{track_id}.json",
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            output,
            fp,
            indent=2
        )

    built += 1

print(
    "turn consensus:",
    built
)
