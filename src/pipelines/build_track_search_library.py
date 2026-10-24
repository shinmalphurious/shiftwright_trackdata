import json

catalog = json.load(
    open(
        "generated/track_catalog.json",
        encoding="utf-8"
    )
)

aliases = json.load(
    open(
        "data/layout_search_aliases.json",
        encoding="utf-8"
    )
)

library = []

for track in catalog:

    track_id = track["track_id"]

    layout = track["layout"]

    parts = layout.split("-")

    venue = parts[1]

    remainder = parts[2:]

    variants = [[]]

    for word in remainder:

        if word in aliases:

            expanded = []

            for existing in variants:

                for alias in aliases[word]:

                    expanded.append(
                        existing + [alias]
                    )

            variants = expanded

        else:

            for existing in variants:

                existing.append(
                    word
                )

    queries = []

    for variant in variants:

        layout_name = " ".join(
            [venue] + variant
        )

    queries.extend(
        [
            {
                "query": f"{layout_name} track guide",
                "priority": 180
            },
            {
                "query": f"{layout_name} lap guide",
                "priority": 170
            },
            {
                "query": f"{layout_name} iracing guide",
                "priority": 160
            },
            {
                "query": f"{layout_name} tutorial",
                "priority": 120
            },
            {
                "query": f"{layout_name} walkthrough",
                "priority": 110
            },
            {
                "query": f"{layout_name} hotlap",
                "priority": 90
            },
            {
                "query": f"{layout_name} hot lap",
                "priority": 90
            },
            {
                "query": f"{layout_name} reference lap",
                "priority": 80
            },
            {
                "query": f"{layout_name} track breakdown",
                "priority": 70
            }
        ]
    )

    library.append(
        {
            "track_id":
                track_id,

            "layout":
                layout,

            "queries":
                queries
        }
    )

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
    "entries:",
    len(library)
)
