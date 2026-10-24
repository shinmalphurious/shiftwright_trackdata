import json

task = json.load(
    open(
        "generated/discovery_task.json",
        encoding="utf-8"
    )
)

result = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

output = {
    "track_id":
        task["track_id"],

    "layout":
        task["layout"],

    "queries":
        task.get(
            "queries",
            []
        ),

    "videos_found":
        len(
            result.get(
                "videos",
                []
            )
        )
}

with open(
    "generated/search_failure_analysis.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        output,
        fp,
        indent=2
    )

print(
    "analysis written"
)
