import json
from pathlib import Path

ROOT = Path(
    r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing"
)

count = 0

for file in ROOT.rglob("commentary.json"):

    try:

        data = json.load(
            open(
                file,
                encoding="utf-8"
            )
        )

        if data.get(
            "track_summary",
            {}
        ):

            count += 1

            print(
                file.parent.name
            )

    except:
        pass

print()
print(
    "tracks_with_youtube:",
    count
)
