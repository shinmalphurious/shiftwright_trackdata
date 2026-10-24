import yt_dlp
import json

video_id = "1Za5r0B4YvE"

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

    if "en" in caps:

        print(
            json.dumps(
                caps["en"],
                indent=2
            )
        )
