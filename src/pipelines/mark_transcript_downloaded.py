import json

queue = json.load(
    open(
        "generated/transcript_queue.json",
        encoding="utf-8"
    )
)

task = json.load(
    open(
        "generated/current_transcript_task.json",
        encoding="utf-8"
    )
)

video_id = task["video_id"]

updated = False

for item in queue:

    if item["video_id"] != video_id:
        continue

    item["status"] = "downloaded"

    updated = True

    break

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
    "downloaded:",
    video_id
)

print(
    "updated:",
    updated
)
