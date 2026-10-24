import json
from pathlib import Path

TRACKS_FILE = Path(
    "registry/tracks.json"
)

LOVELY_FILE = Path(
    "registry/lovely_coverage.json"
)

OUTPUT_FILE = Path(
    "registry/source_coverage.json"
)

with open(
    TRACKS_FILE,
    encoding="utf-8"
) as fp:

    tracks = json.load(fp)

with open(
    LOVELY_FILE,
    encoding="utf-8"
) as fp:

    lovely = json.load(fp)

coverage = {}

for track_id in tracks.keys():

    lovely_data = lovely.get(
        track_id,
        {}
    )

    coverage[track_id] = {

        "track_id": int(
            track_id
        ),

        "map_vector": True,

        "lovely":
            lovely_data.get(
                "lovely_available",
                False
            ),

        "elevation": False,

        "annotations": False
    }

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        coverage,
        fp,
        indent=2
    )

total = len(coverage)

lovely_count = sum(
    1
    for item
    in coverage.values()
    if item["lovely"]
)

print()
print(
    f"Layouts : {total}"
)

print(
    f"Lovely  : {lovely_count}"
)

print(
    f"Coverage: "
    f"{lovely_count/total:.1%}"
)

print()
print(
    f"Wrote {OUTPUT_FILE}"
)
