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
        "knowledge_source",
        {}
    )

    if source.get("type") == "inherited":

        print(
            track_id,
            "->",
            source.get(
                "parent_track_id"
            )
        )
