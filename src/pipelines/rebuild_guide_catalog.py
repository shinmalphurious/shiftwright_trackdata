import json

manifest = json.load(
    open(
        "generated/track_acquisition_manifest.json",
        encoding="utf-8"
    )
)

catalogued = 0

for track in manifest:

    if (
        track["state"]
        !=
        "guides_catalogued"
    ):
        continue

    guide_data = {

        "track_id":
            track["track_id"],

        "layout":
            track["layout"],

        "selected_guides":
            track.get(
                "youtube",
                {}
            ).get(
                "selected_guides",
                {}
            )
    }

    with open(
        f"generated/guide_catalog/{track['track_id']}.json",
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            guide_data,
            fp,
            indent=2
        )

    catalogued += 1

print(
    "archived:",
    catalogued
)
