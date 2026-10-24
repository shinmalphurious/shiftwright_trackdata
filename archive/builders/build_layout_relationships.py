import json
from pathlib import Path

FAMILIES = Path(
    "registry/layout_families.json"
)

OUTPUT = Path(
    "registry/layout_relationships.json"
)

with open(
    FAMILIES,
    encoding="utf-8"
) as fp:
    families = json.load(fp)

relationships = {}

HIGH_CONFIDENCE = [
    "historic",
    "gpchicane",
    "nochicane",
    "2022",
    "2023",
    "2024",
    "2026"
]

MEDIUM_CONFIDENCE = [
    "club",
    "national",
    "short",
    "international"
]

for venue, family in families.items():

    parent = family[
        "canonical_track_id"
    ]

    for layout in family[
        "missing_layouts"
    ]:

        confidence = "low"

        layout_name = (
            layout["layout"] or ""
        ).lower()

        for keyword in HIGH_CONFIDENCE:

            if keyword in layout_name:
                confidence = "high"

        for keyword in MEDIUM_CONFIDENCE:

            if keyword in layout_name:
                confidence = "medium"

        relationships[
            str(layout["track_id"])
        ] = {

            "track_id":
                layout["track_id"],

            "parent_track_id":
                parent,

            "venue": venue,

            "layout":
                layout["layout"],

            "confidence":
                confidence
        }

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        relationships,
        fp,
        indent=2
    )

print(
    f"Relationships: "
    f"{len(relationships)}"
)