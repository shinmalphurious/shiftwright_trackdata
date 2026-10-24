import json

report = json.load(
    open(
        "generated/youtube_coverage_report.json",
        encoding="utf-8"
    )
)

targets = []

for track in report["tracks"]:

    targets.append(
        {
            "track_id":
                track["track_id"],

            "layout":
                track["layout"],

            "state":
                "pending_search",

            "youtube": {
                "videos_found": 0,
                "videos_processed": 0,
                "searches_attempted": 0,
                "video_ids": []
            },

            "knowledge": {
                "transcript_pending": False,
                "transcript_acquired": False,
                "turn_ranges": False,
                "turn_facts": False,
                "knowledge_built": False,

                "source_type": None,
                "parent_track_id": None,

                "search_strategy": "direct_layout",

                "layout_knowledge_found": False,

                "venue_fallback_allowed": True
            }
        }
    )

with open(
    "generated/track_acquisition_manifest.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        targets,
        fp,
        indent=2
    )

print(
    "targets:",
    len(targets)
)






