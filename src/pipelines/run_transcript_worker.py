import json
from datetime import datetime,timedelta,timezone

from src.shared.transcript_backoff import (
    transcript_backoff_minutes
)

queue = json.load(
    open(
        "generated/transcript_queue.json",
        encoding="utf-8"
    )
)

for item in queue:

    if item["status"] != "ready_for_download":
        continue

    item["attempts"] += 1

    item["last_attempt"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    delay = (
        transcript_backoff_minutes(
            item["attempts"]
        )
    )

    item["next_attempt"] = (
        datetime.now(
            timezone.utc
        )
        +
        timedelta(
            minutes=delay
        )
    ).isoformat()

    item["status"] = (
        "rate_limited"
    )

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
    "updated queue"
)
