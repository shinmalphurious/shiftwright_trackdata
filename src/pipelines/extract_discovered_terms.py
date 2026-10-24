import json
from collections import Counter

counter = Counter()

data = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

for video in data["videos"]:

    title = (
        video["title"]
        .lower()
        .replace("|", " ")
        .replace("-", " ")
    )

    words = title.split()

    for word in words:

        if len(word) < 4:
            continue

        counter[word] += 1

with open(
    "generated/discovered_terms.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        dict(counter.most_common(200)),
        fp,
        indent=2
    )

print(
        "terms:",
        len(counter)
)
