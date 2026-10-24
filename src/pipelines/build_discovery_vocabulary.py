import json
from collections import Counter

results = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

terms = Counter()

for video in results["videos"]:

    title = (
        video["title"]
        .lower()
        .replace("|", " ")
        .replace("-", " ")
    )

    for word in title.split():

        if len(word) < 4:
            continue

        terms[word] += 1

with open(
    "generated/discovery_vocabulary.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        dict(
            terms.most_common(200)
        ),
        fp,
        indent=2
    )

print(
        "terms:",
        len(terms)
)
