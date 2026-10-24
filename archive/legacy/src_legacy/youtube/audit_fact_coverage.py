import csv

with open(
    "research/youtube/turn_ranges.csv",
    encoding="utf-16"
) as f:

    rows = list(csv.reader(f))

print(
    "turn ranges:",
    len(rows)
)

matched = 0

with open(
    "research/youtube/turn_facts.csv",
    encoding="utf-16"
) as f:

    facts = [
        x.strip()
        for x in f
        if x.strip()
    ]

print(
    "fact rows:",
    len(facts)
)

print(
    "unmatched:",
    len(rows) - len(facts)
)
