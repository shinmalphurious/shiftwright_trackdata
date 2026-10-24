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

track_id = selection[
    "track_id"
]

for track in manifest:

    if track["track_id"] != track_id:
        continue

    youtube = track.setdefault(
        "youtube",
        {}
    )

    youtube[
        "selected_guides"
    ] = selection[
        "selected_guides"
    ]

    guide_ids = []

    for car,videos in selection[
        "selected_guides"
    ].items():

        for video in videos:

            guide_ids.append(
                video[
                    "video_id"
                ]
            )

    youtube[
        "video_ids"
    ] = sorted(
        set(
            guide_ids
        )
    )

    youtube[
        "videos_found"
    ] = len(
        youtube[
            "video_ids"
        ]
    )

    track[
        "state"
    ] = "guides_catalogued"

    track[
        "knowledge"
    ][
        "transcript_pending"
    ] = True

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
        "stored guides"
)
