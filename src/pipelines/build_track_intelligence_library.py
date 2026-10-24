import json

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

library = []

for track in catalog:

    layout = track["layout"]

    track_id = track["track_id"]

    parts = layout.split("-")

    venue = (
        parts[1]
        if len(parts) > 1
        else layout
    )

    library.append(
        {
            "track_id": track_id,
            "layout": layout,
            "venue": venue,
            "folder": track["folder"],

            "search_topics": [
                "track guide",
                "setup",
                "lap guide",
                "onboard",
                "telemetry",
                "hotlap"
            ],

            "acquisition_status": {
                "youtube": False,
                "garage61": False,
                "setup": False
            }
        }
    )

with open(
    "generated/track_intelligence_library.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        library,
        fp,
        indent=2
    )

print(
    "tracks:",
    len(library)
)
