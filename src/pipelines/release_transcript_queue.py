import json
from datetime import datetime,timezone

queue = json.load(
    open(
        "generated/transcript_queue.json",
        encoding="utf-8"
    )
)

now = datetime.now(
    timezone.utc
)

released = 0

for item in queue:

    if item["status"] != "rate_limited":
        continue

    next_attempt = item.get(
        "next_attempt"
    )

    if not next_attempt:
        continue

    retry_time = datetime.fromisoformat(
        next_attempt
    )

    if retry_time <= now:

        item["status"] = (
            "ready_for_download"
        )

        released += 1

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
    "released:",
    released
)
