import json

targets = json.load(
    open(
        "generated/track_acquisition_manifest.json",
        encoding="utf-8"
    )
)

searches = []

for track in targets:

    layout = track[
        "layout"
    ]

    parts = layout.split("-")

    if len(parts) < 2:
        continue

    search_term = parts[1]

    searches.append(
        {
            "track_id":
                track["track_id"],
            "search_term":
                search_term
        }
    )

with open(
    "generated/search_terms_queue.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        searches,
        fp,
        indent=2
    )

print(
    "search terms:",
    len(searches)
)
