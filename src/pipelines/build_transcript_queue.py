import json
from pathlib import Path

queue = []

for file in Path(
    "generated/guide_catalog"
).glob("*.json"):

    data = json.load(
        open(
            file,
            encoding="utf-8"
        )
    )

    for car,videos in data.get(
        "selected_guides",
        {}
    ).items():

        for video in videos:

            queue.append(
                {
                    "track_id":
                        data["track_id"],

                    "layout":
                        data["layout"],

                    "car":
                        car,

                    "video_id":
                        video["video_id"],

                    "title":
                        video["title"],

                    "status":
                        "ready_for_download",

                    "attempts":
                        0,

                    "last_attempt":
                        None,

                    "next_attempt":
                        None,

                    "caption_format":
                        "json3"
                }
            )

with open(
    "generated/transcript_queue.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        queue,
        fp,
        indent=2
    )

print(
    "queued:",
    len(queue)
)
