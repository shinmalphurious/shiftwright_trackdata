import json
from pathlib import Path

top = []

for file in Path(
    "generated/knowledge_packs"
).glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    count = len(
        data.get(
            "corners",
            []
        )
    )

    top.append(
        (
            count,
            file.stem
        )
    )

top.sort(
    reverse=True
)

print("MOST CORNERS")
print()

for count,track in top[:20]:

    print(
        track,
        count
    )

print()
print("ZERO CORNERS")
print()

zero = sum(
    1
    for count,_ in top
    if count == 0
)

print(zero)
