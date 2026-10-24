import json

manifest = json.load(
    open(
        "generated/track_acquisition_manifest.json",
        encoding="utf-8"
    )
)

for track in manifest:

    if track["state"] != "pending_search":
        continue

    if track.get(
        "youtube",
        {}
    ).get(
        "selected_guides"
    ):
        continue

    with open(
        "generated/current_track.json",
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            track,
            fp,
            indent=2
        )

    print(
        f"claimed: {track['track_id']}"
    )

    break

else:

    print(
        "no pending tracks"
    )
