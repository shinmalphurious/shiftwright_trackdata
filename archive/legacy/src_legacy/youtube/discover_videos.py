import yt_dlp
import csv

SEARCHES = [
    "iRacing Zandvoort track guide",
    "iRacing Spa track guide",
    "iRacing Bathurst track guide",
    "iRacing Road Atlanta track guide"
]

opts = {
    "quiet": True,
    "extract_flat": True
}

with open(
    "research/youtube/catalog/discovered_videos.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "search",
            "video_id",
            "title"
        ]
    )

    with yt_dlp.YoutubeDL(
        opts
    ) as ydl:

        for query in SEARCHES:

            result = ydl.extract_info(
                f"ytsearch20:{query}",
                download=False
            )

            for video in result["entries"]:

                writer.writerow(
                    [
                        query,
                        video["id"],
                        video["title"]
                    ]
                )

print("complete")
