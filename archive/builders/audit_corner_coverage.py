import json
from pathlib import Path

with_corners = 0
without_corners = 0

for file in Path(
    "generated"
).glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    if data.get(
        "corners"
    ):
        with_corners += 1
    else:
        without_corners += 1

print()
print(
    f"With corners: {with_corners}"
)

print(
    f"Without corners: {without_corners}"
)
