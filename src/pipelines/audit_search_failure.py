import json

data = json.load(
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

print()

print(
    "TRACK:",
    data["track_id"]
)

print(
    "LAYOUT:",
    data["layout"]
)

print()

print(
    "QUERY:"
)

print(
    data["query"]
)

print()

print(
    "VIDEOS:",
    len(
        result["videos"]
    )
)
