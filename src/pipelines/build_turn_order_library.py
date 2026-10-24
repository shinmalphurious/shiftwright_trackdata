import csv
import json
from collections import defaultdict
from pathlib import Path

video_turns = defaultdict(list)

with open(
    "research/youtube/turn_ranges.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 3:
            continue

        video_id = row[0]
        turn = row[1].strip()

        if turn not in video_turns[video_id]:

            video_turns[
                video_id
            ].append(
                turn
            )

output = {}

for video_id, turns in video_turns.items():

    output[video_id] = {
        "turn_order": turns,
        "turn_count": len(turns)
    }

with open(
    "generated/turn_order_library.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        output,
        fp,
        indent=2
    )

print(
    "videos:",
    len(output)
)
