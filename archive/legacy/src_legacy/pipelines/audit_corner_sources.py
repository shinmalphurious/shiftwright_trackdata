import json
from pathlib import Path
from collections import Counter

counts = Counter()

for file in Path(
    "generated"
).glob("*.json"):

    try:

        track_id = int(
            file.stem
        )

    except:

        continue

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    source = data.get(
        "source_coverage",
        {}
    )

    lovely = source.get(
        "lovely",
        False
    )

    corners = len(
        data.get(
            "corners",
            []
        )
    )

    if lovely and corners:

        counts["lovely_with_corners"] += 1

    elif lovely:

        counts["lovely_no_corners"] += 1

    elif corners:

        counts["non_lovely_with_corners"] += 1

    else:

        counts["non_lovely_no_corners"] += 1

for k,v in counts.items():

    print(
        k,
        v
    )
