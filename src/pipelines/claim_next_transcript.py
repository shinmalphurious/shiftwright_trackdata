import json
from datetime import datetime,timezone

rate_limit = json.load(
    open(
        "generated/transcript_rate_limit.json",
        encoding="utf-8"
    )
)

pause_until = rate_limit.get(
    "global_pause_until"
)

if pause_until:

    unlock = datetime.fromisoformat(
        pause_until
    )

    if unlock > datetime.now(
        timezone.utc
    ):

        print(
            "GLOBAL_TRANSCRIPT_PAUSE"
        )

        raise SystemExit

queue = json.load(
    open(
        "generated/transcript_queue.json",
        encoding="utf-8"
    )
)

for item in queue:

    if item["status"] != "ready_for_download":
        continue

    item["status"] = "claimed"

    with open(
        "generated/current_transcript_task.json",
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            item,
            fp,
            indent=2
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
        "claimed:",
        item["video_id"]
    )

    raise SystemExit

print(
    "nothing available"
)
