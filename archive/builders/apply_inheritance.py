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

created = 0

for track_id, candidate in candidates.items():

    if candidate[
        "inheritance_level"
    ] not in [
        "high",
        "medium"
    ]:
        continue

    target_file = (
        GENERATED
        / f"{track_id}.json"
    )

    if target_file.exists():
        continue

    parent_file = (
        GENERATED
        / f"{candidate['parent_track_id']}.json"
    )

    if not parent_file.exists():
        continue

    with open(
        parent_file,
        encoding="utf-8"
    ) as fp:

        parent = json.load(fp)

    inherited = {

        "track_id":
            int(track_id),

        "knowledge_source": {

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
        },

        "source_coverage":
            parent.get(
                "source_coverage",
                {}
            ),

        "metadata":
            parent.get(
                "metadata",
                {}
            ),

        "pit":
            parent.get(
                "pit",
                {}
            ),

        "sectors":
            parent.get(
                "sectors",
                []
            ),

        "corners":
            parent.get(
                "corners",
                []
            )
    }

    with open(
        target_file,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            inherited,
            fp,
            indent=2
        )

    created += 1

print()
print(
    f"Created {created} inherited tracks"
)
