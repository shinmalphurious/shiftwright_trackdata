import json

manifest = json.load(
    open(
        "generated/track_acquisition_manifest.json",
        encoding="utf-8"
    )
)

for track in manifest:

    if (
        track["state"] == "videos_found"
        and
        track["knowledge"][
            "knowledge_built"
        ] == False
    ):

        print(
            json.dumps(
                track,
                indent=2
            )
        )

        break
