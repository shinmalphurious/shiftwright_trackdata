import json
from collections import Counter

manifest = json.load(
    open(
        "generated/track_acquisition_manifest.json",
        encoding="utf-8"
    )
)

states = Counter()

for track in manifest:

    states[
        track["state"]
    ] += 1

print()

for state,count in sorted(
    states.items()
):

    print(
        f"{state}: {count}"
    )
