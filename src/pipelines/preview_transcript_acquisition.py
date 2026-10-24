import json

tasks = json.load(
    open(
        "generated/transcript_tasks.json",
        encoding="utf-8"
    )
)

for task in tasks:

    print()

    print(
        task["car"]
    )

    print(
        task["video_id"]
    )

    print(
        task["title"]
    )
