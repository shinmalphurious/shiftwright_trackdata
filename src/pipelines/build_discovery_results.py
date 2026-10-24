import json

task = json.load(
    open(
        "generated/discovery_task.json",
        encoding="utf-8"
    )
)

results = {

    "track_id":
        task["track_id"],

    "layout":
        task["layout"],

    "queries":
        task["queries"],

    "videos": []
}

with open(
    "research/youtube/discovery_results.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        results,
        fp,
        indent=2
    )

print(
    "discovery scaffold created"
)
