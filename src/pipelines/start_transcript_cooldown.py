from pathlib import Path
from datetime import datetime, timedelta

cooldown = Path(
    "generated/transcript_cooldown.txt"
)

if cooldown.exists():

    expires = datetime.fromisoformat(
        cooldown.read_text().strip()
    )

    if expires > datetime.now().astimezone():

        print(
            "cooldown_active"
        )

        raise SystemExit

next_time = (
    datetime.now().astimezone()
    +
    timedelta(
        minutes=30
    )
)

cooldown.write_text(
    next_time.isoformat()
)

print(
    "cooldown_started"
)
