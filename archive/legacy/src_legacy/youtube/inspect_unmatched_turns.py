import csv

fact_keys = set()

with open(
    "research/youtube/turn_facts.csv",
    encoding="utf-16"
) as f:

    for line in f:

        if ":" in line:

            key = (
                line.split(",")[0]
                .strip()
            )

            fact_keys.add(
                key
            )

shown = 0

with open(
    "research/youtube/turn_ranges.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        key = (
            f"{row[0]}:{row[1]}"
        )

        if key not in fact_keys:

            print()
            print(key)
            print(row[2][:500])

            shown += 1

            if shown >= 10:
                break
