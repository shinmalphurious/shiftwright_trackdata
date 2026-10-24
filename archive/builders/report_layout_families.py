import json
from collections import defaultdict

with open(
    "registry/tracks.json",
    encoding="utf-8"
) as fp:
    tracks = json.load(fp)

with open(
    "registry/lovely_coverage.json",
    encoding="utf-8"
) as fp:
    lovely = json.load(fp)

venues = defaultdict(list)

for track_id, layouts in tracks.items():

    layout = layouts[0]

    venues[
        layout["venue_slug"]
    ].append({
        "track_id": int(track_id),
        "layout": layout["layout_slug"],
        "lovely":
            lovely.get(
                track_id,
                {}
            ).get(
                "lovely_available",
                False
            )
    })

for venue in sorted(venues):

    tracks_for_venue = venues[venue]

    lovely_count = sum(
        1 for x in tracks_for_venue
        if x["lovely"]
    )

    if lovely_count == 0:
        continue

    print()
    print(
        f"{venue} "
        f"({lovely_count}/"
        f"{len(tracks_for_venue)})"
    )

    for t in sorted(
        tracks_for_venue,
        key=lambda x: x["track_id"]
    ):

        status = (
            "?"
            if t["lovely"]
            else "?"
        )

        print(
            f"  {status} "
            f"{t['track_id']} "
            f"{t['layout']}"
        )
