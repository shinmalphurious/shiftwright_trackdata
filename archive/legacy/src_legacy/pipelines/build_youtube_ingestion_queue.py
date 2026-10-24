import json

coverage = json.load(
    open(
        "generated/commentary_coverage.json",
        encoding="utf-8"
    )
)

targets = []

for track in coverage:

    if (
        track["geometry"]
        and track["corner_data"]
        and not track["youtube"]
    ):

        targets.append({
            "track_id":
                track["track_id"],

            "layout":
                track["layout"]
        })

targets.sort(
    key=lambda x:
    x["track_id"]
)

with open(
    "generated/youtube_ingestion_queue.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        targets,
        f,
        indent=2
    )

print(
    "tracks needing youtube:",
    len(targets)
)
