import csv
from collections import Counter

keywords = Counter()

with open(
    "research/youtube/turn_ranges.csv",
    encoding="utf-16"
) as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 3:
            continue

        text = row[2].lower()

        for word in [
            "hairpin",
            "slippery",
            "camber",
            "tightens",
            "trail",
            "brake",
            "braking",
            "apex",
            "exit",
            "straight",
            "flat",
            "passing",
            "overtaking",
            "tricky"
        ]:

            if word in text:
                keywords[word] += 1

for word,count in keywords.most_common():
    print(f"{word},{count}")
