import json

selection = json.load(
    open(
        "generated/discovery_selection.json",
        encoding="utf-8"
    )
)

manifest_path = (
    "generated/track_acquisition_manifest.json"
)

manifest = json.load(
    open(
        manifest_path,
        encoding="utf-8"
    )
)

track_id = selection["track_id"]

for track in manifest:

    if track["track_id"] != track_id:
        continue

    youtube = track.setdefault(
        "youtube",
        {}
    )

    youtube["cars"] = (
        selection[
            "selected_guides"
        ]
    )

    youtube["videos_found"] = sum(
        len(v)
        for v in selection[
            "selected_guides"
        ].values()
    )

    if youtube["videos_found"] > 0:

        track["state"] = (
            "videos_found"
        )

    break

with open(
    manifest_path,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        manifest,
        fp,
        indent=2
    )

print(
        "updated"
)
