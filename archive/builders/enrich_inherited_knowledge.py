import json
from pathlib import Path

CANDIDATES = Path(
    "registry/inheritance_candidates.json"
)

GENERATED = Path(
    "generated"
)

with open(
    CANDIDATES,
    encoding="utf-8"
) as fp:

    candidates = json.load(fp)

updated = 0

for track_id, candidate in candidates.items():

    if candidate[
        "inheritance_level"
    ] not in [
        "high",
        "medium"
    ]:
        continue

    child_file = (
        GENERATED
        / f"{track_id}.json"
    )

    parent_file = (
        GENERATED
        / f"{candidate['parent_track_id']}.json"
    )

    if not child_file.exists():
        continue

    if not parent_file.exists():
        continue

    with open(
        child_file,
        encoding="utf-8"
    ) as fp:

        child = json.load(fp)

    with open(
        parent_file,
        encoding="utf-8"
    ) as fp:

        parent = json.load(fp)

    if child.get(
        "corners"
    ):
        continue

    child[
        "knowledge_source"
    ] = {

        "type":
            "inherited",

        "parent_track_id":
            candidate[
                "parent_track_id"
            ],

        "inheritance_level":
            candidate[
                "inheritance_level"
            ]
    }

    child["corners"] = (
        parent.get(
            "corners",
            []
        )
    )

    child["sectors"] = (
        parent.get(
            "sectors",
            []
        )
    )

    child["pit"] = (
        parent.get(
            "pit",
            {}
        )
    )

    with open(
        child_file,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            child,
            fp,
            indent=2
        )

    updated += 1

print()
print(
    f"Enriched: {updated}"
)
