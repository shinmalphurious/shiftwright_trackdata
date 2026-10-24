import json
from pathlib import Path

RELATIONSHIPS_FILE = Path(
    "registry/layout_relationships.json"
)

OUTPUT_FILE = Path(
    "registry/inheritance_candidates.json"
)

with open(
    RELATIONSHIPS_FILE,
    encoding="utf-8"
) as fp:

    relationships = json.load(fp)

candidates = {}

HIGH_INHERIT = [
    "gpchicane",
    "nochicane",
    "historic",
    "2019",
    "2021",
    "2022",
    "2023",
    "2024",
    "2026"
]

MEDIUM_INHERIT = [
    "club",
    "national",
    "international",
    "short",
    "school",
    "bend"
]

LOW_INHERIT = [
    "moto",
    "east",
    "west",
    "north",
    "south",
    "tourist",
    "outer",
    "handling",
    "rallycross"
]

for track_id, rel in relationships.items():

    layout = (
        rel.get("layout")
        or ""
    ).lower()

    inherit_level = "none"

    if rel[
        "confidence"
    ] == "high":
        inherit_level = "high"

    elif rel[
        "confidence"
    ] == "medium":
        inherit_level = "medium"

    for keyword in HIGH_INHERIT:

        if keyword in layout:
            inherit_level = "high"

    for keyword in MEDIUM_INHERIT:

        if keyword in layout:
            if inherit_level == "none":
                inherit_level = "medium"

    for keyword in LOW_INHERIT:

        if keyword in layout:
            inherit_level = "low"

    candidates[track_id] = {

        "track_id":
            rel["track_id"],

        "parent_track_id":
            rel["parent_track_id"],

        "venue":
            rel["venue"],

        "layout":
            rel["layout"],

        "inheritance_level":
            inherit_level,

        "inherit_corners":
            inherit_level
            in ["high", "medium"],

        "inherit_sectors":
            inherit_level
            in ["high", "medium"],

        "inherit_pit":
            inherit_level
            in ["high", "medium"],

        "inherit_track_name":
            True
    }

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        candidates,
        fp,
        indent=2
    )

summary = {
    "high": 0,
    "medium": 0,
    "low": 0,
    "none": 0
}

for item in candidates.values():

    summary[
        item[
            "inheritance_level"
        ]
    ] += 1

print()
print(
    "Inheritance Candidates"
)

for level, count in summary.items():

    print(
        f"{level:<10} "
        f"{count}"
    )

print()
print(
    f"Wrote {OUTPUT_FILE}"
)
