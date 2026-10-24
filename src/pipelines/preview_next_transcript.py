import json

queue = json.load(
    open(
        "generated/transcript_queue.json",
        encoding="utf-8"
    )
)

for item in queue:

    if item["status"] != "ready_for_download":
        continue

    print()

    print(
        "VIDEO:",
        item["video_id"]
    )

    print(
        "TRACK:",
        item["track_id"]
    )

    print(
        "FORMAT:",
        item["caption_format"]
    )

    break
