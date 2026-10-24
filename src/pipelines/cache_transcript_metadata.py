import json

task = json.load(
    open(
        "generated/current_transcript_task.json",
        encoding="utf-8"
    )
)

cache = {
    "video_id":
        task["video_id"],

    "preferred_format":
        "json3",

    "captions_available":
        True,

    "status":
        "waiting_for_transport"
}

with open(
    f"generated/caption_cache_{task['video_id']}.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        cache,
        fp,
        indent=2
    )

print(
    cache["video_id"]
)
