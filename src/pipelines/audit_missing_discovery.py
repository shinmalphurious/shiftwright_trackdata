import json

manifest = json.load(
    open(
        "generated/track_acquisition_manifest.json",
        encoding="utf-8"
    )
)

for track in manifest:

    if track["state"] != "guides_catalogued":
        continue

    youtube = track.get(
        "youtube",
        {}
    )

    videos_found = youtube.get(
        "videos_found",
        0
    )

    if videos_found == 0:

        print()

        print(
            track["track_id"],
            track["layout"]
        )
