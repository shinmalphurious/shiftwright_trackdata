import json
from pathlib import Path

with open(
    "registry/inheritance_candidates.json",
    encoding="utf-8"
) as fp:
    candidates = json.load(fp)

available = 0
blocked = 0

for _, candidate in candidates.items():

    if candidate[
        "inheritance_level"
    ] not in [
        "high",
        "medium"
    ]:
        continue

    parent_file = Path(
        "generated"
    ) / f"{candidate['parent_track_id']}.json"

    if not parent_file.exists():
        blocked += 1
        continue

    data = json.load(
        open(
            parent_file,
            encoding="utf-8"
        )
    )

    if data.get("corners"):
        available += 1
    else:
        blocked += 1

print()
print(
    f"Can inherit: {available}"
)

print(
    f"Blocked: {blocked}"
)
