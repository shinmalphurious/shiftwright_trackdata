import json
import yt_dlp
import sys

print(sys.executable)

vehicle_lookup = json.load(
    open(
        "generated/vehicle_lookup.json",
        encoding="utf-8"
    )
)

task = json.load(
    open(
        "generated/discovery_task.json",
        encoding="utf-8"
    )
)

queries = task.get(
    "queries",
    []
)

from src.shared.ytdlp_config import YT_DLP_OPTIONS

opts = dict(YT_DLP_OPTIONS)

opts.update({

    "quiet": True,
    "extract_flat": True,
    "socket_timeout": 15,
    "extractor_retries": 1
})


videos = []
successful_query = None

with yt_dlp.YoutubeDL(opts) as ydl:

    for query_obj in queries:

        query = query_obj["query"]

        try:

            result = ydl.extract_info(
                f"ytsearch10:{query}",
                download=False
            )

        except Exception:

            continue

        entries = result.get(
            "entries",
            []
        )

        if not entries:

            continue

        successful_query = query

        print(
            "SUCCESSFUL_QUERY:",
            query
        )

        for video in entries:

            title = video.get(
                "title",
                ""
            )

            description = (
                video.get(
                    "description",
                    ""
                ) or ""
            )

            lower = (
                title + " " + description
            ).lower()

            car = None

            for alias,canonical in vehicle_lookup.items():

                if alias in lower:

                    car = canonical

                    break

            if (
                "track guide" in lower
                or "lap guide" in lower
                or "guide" in lower
            ):
                video_type = "lap_walkthrough"
            else:
                video_type = "other"

            score = 0

            if video_type == "lap_walkthrough":
                score += 100

            if "iracing" in lower:
                score += 100

            if car:
                score += 20

            videos.append(
                {
                    "video_id": video.get("id"),
                    "title": title,
                    "description": description,
                    "video_type": video_type,
                    "car": car,
                    "quality_score": score
                }
            )

        break

videos.sort(
    key=lambda v: v["quality_score"],
    reverse=True
)

output = {
    "track_id": task["track_id"],
    "layout": task["layout"],
    "query": successful_query,
    "videos": videos
}


with open(
    "generated/discovery_result.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        output,
        fp,
        indent=2
    )

print("SUCCESSFUL_QUERY:", successful_query)
print("videos found:", len(videos))



