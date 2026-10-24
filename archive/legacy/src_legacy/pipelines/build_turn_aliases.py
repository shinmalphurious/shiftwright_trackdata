import json
import re

track = json.load(
    open(
        "generated/corner_research_registry.json",
        encoding="utf-8"
    )
)

road_atlanta = track["127"]

print()

for corner in road_atlanta["corners"]:

    name = corner["corner_name"]

    m = re.search(
        r"turn\s*(\d+[A-Z]?)",
        name,
        re.IGNORECASE
    )

    if m:

        print(
            f"turn_{m.group(1).lower()} -> {name}"
        )
