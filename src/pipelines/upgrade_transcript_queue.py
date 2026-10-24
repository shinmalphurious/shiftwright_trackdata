import json

queue = json.load(
    open(
        "generated/transcript_queue.json",
        encoding="utf-8"
    )
)

for item in queue:

    item.setdefault(
        "captions_available",
        True
    )

    item.setdefault(
        "preferred_format",
        "json3"
    )

    item.setdefault(
        "last_checked",
        None
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
    "updated:",
    len(queue)
)
