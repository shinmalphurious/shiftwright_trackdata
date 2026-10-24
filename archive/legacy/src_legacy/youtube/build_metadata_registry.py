import csv
import re

with open(
    "research/youtube/catalog/discovered_videos.csv",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        title = row["title"]

        track = "unknown"

        for candidate in [
            "Zandvoort",
            "Spa",
            "Bathurst",
            "Road Atlanta"
        ]:

            if candidate.lower() in title.lower():
                track = candidate
                break

        safe_title = (
            title.encode(
                "ascii",
                errors="ignore"
            )
            .decode("ascii")
        )

        print(
            f"{row['video_id']},{track},{safe_title}"
        )
