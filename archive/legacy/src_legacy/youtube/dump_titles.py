import csv

with open(
    "research/youtube/catalog/discovered_videos.csv",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        title = row["title"]

        print()

        print(
            row["video_id"]
        )

        print(
            title
        )
