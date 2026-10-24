import json

queue = json.load(
    open(
        "generated/transcript_queue.json",
        encoding="utf-8"
    )
)

registry = {}

for item in queue:

    registry[
        item["video_id"]
    ] = {
        "captions_available":
            True,

        "preferred_format":
            "json3",

        "status":
            item["status"]
    }

with open(
    "generated/caption_registry.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        registry,
        fp,
        indent=2
    )

print(
        "videos:",
        len(registry)
)
