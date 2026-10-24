import json

task = json.load(
    open(
        "generated/discovery_task.json",
        encoding="utf-8"
    )
)

query = task["query"]["query"]

result = {
    "track_id":
        task["track_id"],

    "layout":
        task["layout"],

    "query":
        query,

    "videos": []
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
    "query ready:"
)

print(
    query
)
