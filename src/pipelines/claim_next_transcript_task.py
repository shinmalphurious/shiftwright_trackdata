import json

tasks = json.load(
    open(
        "generated/transcript_tasks.json",
        encoding="utf-8"
    )
)

for task in tasks:

    if task["state"] != "pending":
        continue

    print(
        json.dumps(
            task,
            indent=2
        )
    )

    break

else:

    print(
        "no transcript work"
    )
