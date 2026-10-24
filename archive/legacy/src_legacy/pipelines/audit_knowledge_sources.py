import json
from pathlib import Path

count = 0

for file in Path(
    "generated"
).glob("*.json"):

    try:
        int(file.stem)
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

    if source:

        count += 1

        print(
            file.stem,
            source
        )

print()
print(
    "tracks_with_knowledge_source:",
    count
)
