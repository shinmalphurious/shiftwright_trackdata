import csv
from collections import defaultdict

FACT_PATTERNS = {

    "braking_50m": [
        "50 board",
        "50m board",
        "50 m board"
    ],

    "braking_100m": [
        "100 board",
        "100m board",
        "100 m board"
    ],

    "braking_200m": [
        "200 board",
        "200 sign",
        "200 marker"
    ],

    "trail_braking": [
        "trail it off",
        "trail brake",
        "trail braking",
        "long trail off"
    ],

    "early_throttle": [
        "back on the gas",
        "pick back up on the gas",
        "early on throttle",
        "100% at the apex",
        "100% before the apex"
    ],

    "slippery": [
        "slippery",
        "slippy"
    ],

    "cambered": [
        "camber",
        "cambered",
        "off camber"
    ],

    "hairpin": [
        "hairpin"
    ],

    "important_exit": [
        "carry speed",
        "important exit",
        "long straight",
        "passing opportunity"
    ],

    "tightening_corner": [
        "continually tightens",
        "tightens"
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
        text = row[2].lower()

        key = f"{video_id}:{turn}"

        for fact,patterns in FACT_PATTERNS.items():

            if any(
                p in text
                for p in patterns
            ):
                facts[key].add(fact)

for key in sorted(facts):

    print(
        key,
        ",",
        ",".join(
            sorted(
                facts[key]
            )
        )
    )
