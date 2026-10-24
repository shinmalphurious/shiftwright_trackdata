import json
import subprocess
import sys

PYTHON = sys.executable

payload = json.loads(
    subprocess.check_output(
        [
            PYTHON,
            "-m",
            "src.pipelines.build_search_payload"
        ],
        text=True
    )
)

queries = list(
    payload["queries"]
)

venue = (
    payload["layout"]
    .split("-")[1]
)

queries.extend(
    [
        {
            "query":
                f"{venue} track guide",
            "priority":
                20
        },
        {
            "query":
                f"{venue} lap guide",
            "priority":
                15
        },
        {
            "query":
                f"{venue} iracing guide",
            "priority":
                10
        }
    ]
)

task = {
    "track_id":
        payload["track_id"],

    "layout":
        payload["layout"],

    "queries":
        queries
}

with open(
    "generated/discovery_task.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        task,
        fp,
        indent=2
    )

print(
        json.dumps(
            task,
            indent=2
        )
)
