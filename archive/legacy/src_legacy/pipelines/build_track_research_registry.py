import json

TRACKS = {
    127: ("Road Atlanta",20),
    219: ("Bathurst",18),
    485: ("Zandvoort",20),
    525: ("Spa",20)
}

report = []

for track_id,(name,videos) in TRACKS.items():

    data = json.load(
        open(
            f"generated/{track_id}.json",
            encoding="utf-8"
        )
    )

    corners = len(
        data.get(
            "corners",
            []
        )
    )

    report.append(
        {
            "track_id": track_id,
            "track_name": name,
            "youtube_videos": videos,
            "corner_count": corners,
            "video_per_corner":
                round(
                    videos / corners,
                    2
                )
        }
    )

with open(
    "generated/track_research_registry.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        report,
        f,
        indent=2
    )

print("complete")
