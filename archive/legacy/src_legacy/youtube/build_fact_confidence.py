import csv
from collections import defaultdict, Counter

corner_facts = defaultdict(Counter)

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

        _,turn = left.split(
            ":",
            1
        )

        for fact in right.split(","):

            fact = fact.strip()

            if fact:
                corner_facts[turn][fact] += 1

print()

for turn,facts in sorted(corner_facts.items()):

    total = sum(facts.values())

    print(f"{turn}")

    for fact,count in facts.most_common():

        confidence = round(
            count / total,
            2
        )

        print(
            f"  {fact}: {count} ({confidence})"
        )

    print()
