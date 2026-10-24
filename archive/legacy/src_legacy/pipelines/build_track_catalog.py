import json
from pathlib import Path

ROOT = Path(
    r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing"
)

tracks = []

for turns_svg in ROOT.rglob("turns.svg"):

    folder = turns_svg.parent

    layout = folder.name

    try:
        track_id = int(
            layout.split("-")[0]
        )
    except:
        continue

    tracks.append({

        "track_id": track_id,

        "layout": layout,

        "folder": str(folder),

        "has_active_svg":
            (folder / "active.svg").exists(),

        "has_turns_svg": True,

        "has_commentary":
            (folder / "commentary.json").exists()
    })

tracks.sort(
    key=lambda x: x["track_id"]
)

with open(
    "generated/track_catalog.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        tracks,
        f,
        indent=2
    )

print(
    "tracks:",
    len(tracks)
)
