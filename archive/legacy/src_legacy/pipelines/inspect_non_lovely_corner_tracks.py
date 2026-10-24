import json
from pathlib import Path

for file in Path(
    "generated"
).glob("*.json"):

    try:
        track_id = int(file.stem)
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

    if (not lovely) and corners:

        print(
            track_id,
            corners
        )
