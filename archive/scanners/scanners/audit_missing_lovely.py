import json
from pathlib import Path

with open(
    "registry/lovely_coverage.json",
    encoding="utf-8"
) as fp:
    coverage = json.load(fp)

missing = [
    x for x in coverage.values()
    if not x["lovely_available"]
]

print(f"Missing: {len(missing)}")
print()

for item in missing[:100]:
    print(
        item["track_id"]
    )
