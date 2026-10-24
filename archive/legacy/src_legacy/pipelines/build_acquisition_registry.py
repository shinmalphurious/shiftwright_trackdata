import json

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

registry = {}

for track in catalog:

    track_id = str(
        track["track_id"]
    )

    registry[track_id] = {

        "layout":
            track["layout"],

        "youtube": {

            "status":
                "pending",

            "videos_found": 0,

            "videos_processed": 0
        },

        "garage61": {

            "status":
                "pending"
        },

        "telemetry": {

            "status":
                "pending"
        }
    }

with open(
    "generated/acquisition_registry.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        registry,
        f,
        indent=2
    )

print(
    "created",
    len(registry),
    "registry entries"
)
