import csv
import json
from collections import defaultdict, Counter

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

track_facts = defaultdict(Counter)

with open(
    "research/youtube/turn_facts_v2.csv",
    encoding="utf-16"
) as f:

    for line in f:

        if ":" not in line:
            continue

        left, right = line.strip().split(
            ",",
            1
        )

        video_id, turn = left.split(
            ":",
            1
        )

        track = video_track.get(
            video_id
        )

        if not track:
            continue

        for fact in right.split(","):

            fact = fact.strip()

            if fact:

                track_facts[
                    track
                ][fact] += 1

output = {}

for track, facts in sorted(
    track_facts.items()
):

    output[track] = dict(
        facts.most_common()
    )

with open(
    "research/youtube/track_fact_summary.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        output,
        fp,
        indent=2
    )

print(
    "track summaries:",
    len(output)
)
