import json
from datetime import datetime,timedelta,timezone

state = {
    "last_429":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "global_pause_until":
        (
            datetime.now(
                timezone.utc
            ) +
            timedelta(
                hours=6
            )
        ).isoformat()
}

with open(
    "generated/transcript_rate_limit.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        state,
        fp,
        indent=2
    )

print(
    json.dumps(
        state,
        indent=2
    )
)
