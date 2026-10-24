import yt_dlp
import json

task = json.load(
    open(
        "generated/current_transcript_task.json",
        encoding="utf-8"
    )
)

video_id = task[
    "video_id"
]

with yt_dlp.YoutubeDL(
    {
        "quiet": True,
        "skip_download": True
    }
) as ydl:

    info = ydl.extract_info(
        f"https://www.youtube.com/watch?v={video_id}",
        download=False
    )

caps = (
    info.get(
        "automatic_captions",
        {}
    )
)

output = {
    "video_id":
        video_id,

    "languages":
        list(
            caps.keys()
        )
}

with open(
    f"generated/caption_capabilities_{video_id}.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        output,
        fp,
        indent=2
    )

print(
    "languages:",
    len(
        output["languages"]
    )
)
