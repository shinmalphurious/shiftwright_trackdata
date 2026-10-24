import json
from pathlib import Path

missing = []

for file in Path(
    "generated/knowledge_packs"
).glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    if not data.get(
        "corners",
        []
    ):

        missing.append(
            int(file.stem)
        )

with open(
    "generated/missing_corner_models.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        sorted(missing),
        f,
        indent=2
    )

print(
    "missing corner models:",
    len(missing)
)
