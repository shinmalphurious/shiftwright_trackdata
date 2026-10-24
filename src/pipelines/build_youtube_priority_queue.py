import json

report = json.load(
    open(
        "generated/youtube_coverage_report.json",
        encoding="utf-8"
    )
)

tracks = report[
    "tracks"
]

tracks.sort(
    key=lambda x: x["track_id"]
)

with open(
    "generated/youtube_priority_queue.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        tracks,
        fp,
        indent=2
    )

print(
    "targets:",
    len(tracks)
)
