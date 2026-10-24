from __future__ import annotations

import csv

with open(
    "inherited_tracks.csv",
    "r",
    encoding="utf-16"
) as f:

    for row in csv.reader(f):

        if not row:
            continue

        track_id = row[0]
        parent_id = row[1]
        level = row[2]

        generated = int(row[3])
        named = int(row[4])

        diff = abs(
            generated - named
        )

        if diff <= 3:

            print(
                f"{track_id},"
                f"{parent_id},"
                f"{level},"
                f"{generated},"
                f"{named},"
                f"{diff}"
            )
