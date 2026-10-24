from pathlib import Path
import json
import re

VECTOR_ROOT = Path(
    r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing"
)

tracks = {}

for category_dir in VECTOR_ROOT.iterdir():

    if not category_dir.is_dir():
        continue

    category = category_dir.name

    for venue_dir in category_dir.iterdir():

        if not venue_dir.is_dir():
            continue

        for layout_dir in venue_dir.iterdir():

            if not layout_dir.is_dir():
                continue

            m = re.match(
                r"^(\d+)-",
                layout_dir.name
            )

            if not m:
                continue

            track_id = m.group(1)

            tracks[track_id] = {
                "category": category,
                "venue": venue_dir.name
            }

with open(
    "registry/track_categories.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        tracks,
        fp,
        indent=2
    )

print(
    f"Wrote {len(tracks)} categories"
)
