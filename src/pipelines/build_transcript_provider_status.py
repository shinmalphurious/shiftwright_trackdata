import json

status = {
    "youtube_transcript_api":
        "blocked",

    "youtube_caption_endpoint":
        "429",

    "caption_metadata":
        "working",

    "ready_for_download":
        76
}

with open(
    "generated/transcript_provider_status.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        status,
        fp,
        indent=2
    )

print(
        json.dumps(
            status,
            indent=2
        )
)
