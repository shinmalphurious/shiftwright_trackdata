import json

registry = json.load(
    open(
        "generated/acquisition_registry.json",
        encoding="utf-8"
    )
)

complete = 0
pending = 0

for track in registry.values():

    if (
        track["youtube"]["status"]
        == "complete"
    ):
        complete += 1
    else:
        pending += 1

print(
    "youtube_complete:",
    complete
)

print(
    "youtube_pending:",
    pending
)
