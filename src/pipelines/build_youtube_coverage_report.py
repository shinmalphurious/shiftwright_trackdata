import json

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

video_registry = json.load(
    open(
        "generated/video_track_registry.json",
        encoding="utf-8"
    )
)

covered = set()

for video in video_registry.values():

    track_id = video.get(
        "track_id"
    )

    if track_id:
        covered.add(track_id)

missing = []

for track in catalog:

    track_id = track[
        "track_id"
    ]

    if track_id not in covered:

        missing.append(
            track
        )

with open(
    "generated/youtube_coverage_report.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        {
            "covered":
                len(covered),
            "missing":
                len(missing),
            "tracks":
                missing
        },
        fp,
        indent=2
    )

print(
    "covered:",
    len(covered)
)

print(
    "missing:",
    len(missing)
)
