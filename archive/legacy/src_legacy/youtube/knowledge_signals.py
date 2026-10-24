import csv
from collections import Counter

patterns = {
    "slippery" : [
        "slippery",
        "slippy"
    ],

    "trail_brake" : [
        "trail it off",
        "trail brake",
        "trail braking"
    ],

    "early_throttle" : [
        "back on the gas",
        "pick back up on the gas",
        "100% before the apex"
    ],

    "important_exit" : [
        "carry speed",
        "important exit",
        "down the straight"
    ],

    "cambered" : [
        "cambered",
        "camber"
    ]
}

counter = Counter()

with open(
    "research/youtube/turn_ranges.csv",
    encoding="utf-16"
) as f:

    for line in f:

        lower = line.lower()

        for category, terms in patterns.items():

            if any(
                term in lower
                for term in terms
            ):
                counter[category] += 1

for category,count in counter.most_common():

    print(
        f"{category},{count}"
    )
