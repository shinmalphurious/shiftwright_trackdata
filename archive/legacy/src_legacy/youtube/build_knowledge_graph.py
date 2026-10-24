import csv
import json
from collections import defaultdict

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

knowledge = defaultdict(
    lambda: {
        "videos": set(),
        "facts": set()
    }
)

with open(
    "research/youtube/turn_facts.csv",
    encoding="utf-16"
) as f:

    for line in f:

        line = line.strip()

        if ":" not in line:
            continue

        left,right = line.split(
            ",",
            1
        )

        video_id,turn = left.split(
            ":",
            1
        )

        track = video_track.get(
            video_id
        )

        if not track:
            continue

        key = f"{track}:{turn}"

        knowledge[key]["videos"].add(
            video_id
        )

        for fact in right.split(","):

            fact = fact.strip()

            if fact:
                knowledge[key]["facts"].add(
                    fact
                )

output = []

for key,data in knowledge.items():

    track,turn = key.split(
        ":",
        1
    )

    output.append({
        "track": track,
        "turn": turn,
        "supporting_videos":
            len(data["videos"]),
        "facts":
            sorted(
                data["facts"]
            )
    })

with open(
    "research/youtube/knowledge_graph.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        indent=2
    )

print(
    f"generated {len(output)} nodes"
)
