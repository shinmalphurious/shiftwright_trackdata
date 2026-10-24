import json

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

failed = []

for track in catalog:

    layout = track["layout"]

    if any(
        token in layout
        for token in [
            "outerinner",
            "figureeight",
            "figureeightjump",
            "roada",
            "roadb",
            "roadc"
        ]
    ):

        failed.append(
            {
                "track_id":
                    track["track_id"],

                "layout":
                    layout
            }
        )

with open(
    "generated/layout_alias_review.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        failed,
        fp,
        indent=2
    )

print(
        "layouts:",
        len(failed)
)
