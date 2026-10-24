import json
from pathlib import Path

selection = json.load(
    open(
        "generated/discovery_selection.json",
        encoding="utf-8"
    )
)

transcript_dir = Path(
    "research/youtube/transcripts"
)

tasks = []

for car,videos in selection[
    "selected_guides"
].items():

    for video in videos:

        video_id = video[
            "video_id"
        ]

        transcript_exists = (
            transcript_dir /
            f"{video_id}.json"
        ).exists()

        tasks.append(
            {
                "track_id":
                    selection[
                        "track_id"
                    ],

                "layout":
                    selection[
                        "layout"
                    ],

                "car":
                    car,

                "video_id":
                    video_id,

                "title":
                    video[
                        "title"
                    ],

                "state":
                    (
                        "complete"
                        if transcript_exists
                        else "pending"
                    )
            }
        )

with open(
    "generated/transcript_tasks.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        tasks,
        fp,
        indent=2
    )

print(
        "tasks:",
        len(tasks)
)
