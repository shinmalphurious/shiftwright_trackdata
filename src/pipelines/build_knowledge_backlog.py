import json

coverage = json.load(
    open(
        "generated/discovery_effectiveness.json",
        encoding="utf-8"
    )
)

work = []

for track in coverage:

    if track["guides"] == 0:

        continue

    work.append(
        {
            "track_id":
                track["track_id"],

            "layout":
                track["layout"],

            "guides":
                track["guides"],

            "cars":
                track["cars"],

            "priority":
                (
                    track["guides"]
                    *
                    track["cars"]
                )
        }
    )

work.sort(
    key=lambda x:
        x["priority"],
    reverse=True
)

with open(
    "generated/knowledge_backlog.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        work,
        fp,
        indent=2
    )

print(
        "tracks:",
        len(work)
)
