import json
from pathlib import Path
from collections import defaultdict

TRACKS_FILE = Path(
    "registry/tracks.json"
)

LOVELY_FILE = Path(
    "registry/lovely_coverage.json"
)

OUTPUT_FILE = Path(
    "registry/layout_families.json"
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

families = defaultdict(
    lambda: {
        "venue": None,
        "canonical_track_id": None,
        "covered_layouts": [],
        "missing_layouts": []
    }
)

for track_id, layouts in tracks.items():

    layout = layouts[0]

    venue = layout["venue_slug"]

    family = families[venue]

    family["venue"] = venue

    item = {
        "track_id": int(track_id),
        "layout": layout["layout_slug"],
        "folder_name": layout["folder_name"]
    }

    has_lovely = (
        lovely.get(
            track_id,
            {}
        ).get(
            "lovely_available",
            False
        )
    )

    if has_lovely:

        family[
            "covered_layouts"
        ].append(item)

        if (
            family[
                "canonical_track_id"
            ] is None
        ):
            family[
                "canonical_track_id"
            ] = int(track_id)

    else:

        family[
            "missing_layouts"
        ].append(item)

for venue, family in families.items():

    if family["canonical_track_id"] is not None:
        continue

    layouts = sorted(
        family["missing_layouts"],
        key=lambda x: x["track_id"]
    )

    if layouts:
        family[
            "canonical_track_id"
        ] = layouts[0][
            "track_id"
        ]

layout_families = dict(
    sorted(
        families.items()
    )
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        layout_families,
        fp,
        indent=2
    )

covered_families = sum(
    1
    for x
    in layout_families.values()
    if x["covered_layouts"]
)

print()
print(
    f"Venue families: "
    f"{len(layout_families)}"
)

print(
    f"Families with Lovely: "
    f"{covered_families}"
)

print()
print(
    f"Wrote {OUTPUT_FILE}"
)
