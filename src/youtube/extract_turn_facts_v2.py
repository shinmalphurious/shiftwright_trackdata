import csv
from collections import defaultdict

FACT_WORDS = {
    "braking_zone": [
        "brake",
        "braking"
    ],
    "trail_braking": [
        "trail"
    ],
    "apex_focus": [
        "apex"
    ],
    "exit_focus": [
        "exit"
    ],
    "long_straight": [
        "straight"
    ],
    "flat_corner": [
        "flat"
    ],
    "hairpin": [
        "hairpin"
    ],
    "cambered": [
        "camber"
    ],
    "slippery": [
        "slippery",
        "slippy"
    ]
}

facts = defaultdict(set)

with open(
    "research/youtube/turn_ranges.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 3:
            continue

        video_id = row[0]
        turn = row[1]
        sequence = row[2]
        start_idx = row[3]
        end_idx = row[4]
        text = row[5].lower()

        key = (
            f"{video_id}|"
            f"{turn}|"
            f"{sequence}|"
            f"{start_idx}|"
            f"{end_idx}"
        )

        for fact,words in FACT_WORDS.items():

            if any(word in text for word in words):

                facts[key].add(fact)

for key in sorted(facts):

    print(
        key,
        ",",
        ",".join(
            sorted(facts[key])
        )
    )



