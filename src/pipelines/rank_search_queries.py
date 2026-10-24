import json

library = json.load(
    open(
        "generated/track_search_library.json",
        encoding="utf-8"
    )
)

for entry in library:

    ranked = []

    for query in entry["queries"]:

        score = 0

        if "track guide" in query:
            score += 100

        if "lap guide" in query:
            score += 90

        if "guide" in query:
            score += 80

        if "setup" in query:
            score += 40

        if "onboard" in query:
            score += 30

        ranked.append(
            {
                "query": query,
                "priority": score
            }
        )

    ranked.sort(
        key=lambda x: x["priority"],
        reverse=True
    )

    entry["queries"] = ranked

with open(
    "generated/track_search_library.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        library,
        fp,
        indent=2
    )

print(
    "ranked:",
    len(library)
)
