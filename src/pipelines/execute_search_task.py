import json

payload = json.loads(
    __import__(
        "subprocess"
    ).check_output(
        [
            "python",
            "-m",
            "src.pipelines.build_search_payload"
        ],
        text=True
    )
)

print()
print("TRACK")
print(payload["track_id"])

print()
print("SEARCH TERMS")

for query in payload["queries"]:

    print(
        "-",
        query
    )

print()
print(
    "READY_FOR_DISCOVERY"
)
