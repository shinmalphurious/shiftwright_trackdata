import json

task = json.load(
    open(
        "generated/discovery_task.json",
        encoding="utf-8"
    )
)

result = {
    "track_id":
        task["track_id"],

    "layout":
        task["layout"],

    "query":
        task["query"],

    "videos": [
        {
            "video_id": "",
            "title": "",
            "video_type": ""
        }
    ]
}

with open(
    "generated/discovery_result.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        result,
        fp,
        indent=2
    )

print(
    "template created"
)
