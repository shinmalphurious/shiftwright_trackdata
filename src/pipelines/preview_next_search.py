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

    track_id = track["track_id"]

    layout = track["layout"]

    print()
    print("TRACK")
    print(track_id)

    print()
    print("LAYOUT")
    print(layout)

    print()
    print("SEARCHES")

    print(
        layout.replace(
            "-",
            " "
        )
    )

    print(
        f"{layout} track guide"
    )

    print(
        f"{layout} iracing"
    )

    break
