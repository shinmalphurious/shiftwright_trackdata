import json
from pathlib import Path

manifest_path = (
    "generated/track_acquisition_manifest.json"
)

manifest = json.load(
    open(
        manifest_path,
        encoding="utf-8"
    )
)

knowledge_dir = Path(
    "generated/youtube_knowledge"
)

updated = 0

for track in manifest:

    track_id = track[
        "track_id"
    ]

    knowledge_file = (
        knowledge_dir /
        f"{track_id}.json"
    )

    if knowledge_file.exists():

        knowledge = json.load(
            open(
                knowledge_file,
                encoding="utf-8"
            )
        )

        track[
            "knowledge"
        ][
            "knowledge_built"
        ] = True

        track[
            "knowledge"
        ][
            "track_fact_count"
        ] = len(
            knowledge.get(
                "track_summary",
                {}
            )
        )

        track[
            "knowledge"
        ][
            "turn_count"
        ] = len(
            knowledge.get(
                "turn_consensus",
                {}
            )
        )

        track[
            "knowledge"
        ][
            "cars"
        ] = sorted(
            list(
                {
                    video.get("car")
                    for video in knowledge.get(
                        "videos",
                        []
                    )
                    if video.get("car")
                }
            )
        )

        track[
            "state"
        ] = "knowledge_built"

    updated += 1

with open(
    manifest_path,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        manifest,
        fp,
        indent=2
    )

print(
    "tracks updated:",
    updated
)


