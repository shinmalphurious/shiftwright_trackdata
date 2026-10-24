import json

track = json.load(
    open(
        "generated/current_track.json",
        encoding="utf-8"
    )
)

search_library = {
    item["track_id"]: item
    for item in json.load(
        open(
            "generated/track_search_library.json",
            encoding="utf-8"
        )
    )
}

entry = search_library.get(
    track["track_id"]
)

if not entry:

    raise SystemExit(
        "track not found in search library"
    )

payload = {
    "track_id":
        track["track_id"],

    "layout":
        track["layout"],

    "queries":
        entry["queries"],

    "search_strategy":
        track["knowledge"][
            "search_strategy"
        ]
}

print(
    json.dumps(
        payload,
        indent=2
    )
)
