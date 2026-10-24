import json

coverage = json.load(
    open(
        "generated/commentary_coverage.json",
        encoding="utf-8"
    )
)

road_tracks = []

for track in coverage:

    if not track["youtube"]:

        road_tracks.append(
            {
                "track_id":
                    track["track_id"],

                "layout":
                    track["layout"]
            }
        )

road_tracks.sort(
    key=lambda x:
    x["layout"]
)

with open(
    "generated/priority_youtube_targets.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        road_tracks,
        f,
        indent=2
    )

print(
    "targets:",
    len(road_tracks)
)
