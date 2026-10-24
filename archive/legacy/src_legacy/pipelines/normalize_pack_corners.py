import json
from pathlib import Path

updated = 0

for file in Path(
    "generated/knowledge_packs"
).glob("*.json"):

    pack = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    corners = []

    named = pack.get(
        "named_corners",
        []
    )

    if named:

        for i,corner in enumerate(
            named,
            start=1
        ):

            corners.append({

                "corner_id": i,

                "name":
                    corner.get(
                        "name"
                    ),

                "start_pct":
                    corner.get(
                        "start_pct"
                    ),

                "end_pct":
                    corner.get(
                        "end_pct"
                    ),

                "source":
                    "named"
            })

    else:

        for i,corner in enumerate(
            pack.get(
                "generated_corner_regions",
                []
            ),
            start=1
        ):

            corners.append({

                "corner_id": i,

                "name":
                    f"Corner {i}",

                "start_pct":
                    corner.get(
                        "start_pct"
                    ),

                "apex_pct":
                    corner.get(
                        "apex_pct"
                    ),

                "end_pct":
                    corner.get(
                        "end_pct"
                    ),

                "strength":
                    corner.get(
                        "strength"
                    ),

                "source":
                    "generated"
            })

    pack["corners"] = corners

    with open(
        file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            pack,
            f,
            indent=2
        )

    updated += 1

print(
    "normalized",
    updated,
    "packs"
)
