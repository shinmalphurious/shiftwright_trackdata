import csv
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

consensus = defaultdict(Counter)

with open(
    "research/youtube/turn_facts_v2.csv",
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
            video_id,
            "unknown"
        )

        key = f"{track}:{turn}"

        for fact in right.split(","):

            fact = fact.strip()

            if fact:
                consensus[key][fact] += 1

for key in sorted(consensus):

    print()
    print(key)

    for fact,count in consensus[key].most_common():

        print(
            f"  {fact}: {count}"
        )
