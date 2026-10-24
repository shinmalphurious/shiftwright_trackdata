import json
from pathlib import Path
from collections import Counter

counter = Counter()

for file in Path(
    "generated/guide_catalog"
).glob(
    "*.json"
):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    for car,videos in data.get(
        "selected_guides",
        {}
    ).items():

        for video in videos:

            title = (
                video["title"]
                .lower()
            )

            for token in title.split():

                if len(token) < 4:
                    continue

                counter[token] += 1

with open(
    "generated/discovered_vocabulary.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        dict(
            counter.most_common(500)
        ),
        fp,
        indent=2
    )

print(
        "terms:",
        len(counter)
)
