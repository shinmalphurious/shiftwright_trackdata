import json
import yt_dlp

from src.shared.ytdlp_config import (
    YT_DLP_OPTIONS
)

video_id = "1Za5r0B4YvE"

url = (
    f"https://www.youtube.com/watch?v={video_id}"
)

opts = dict(
    YT_DLP_OPTIONS
)

opts["skip_download"] = True

with yt_dlp.YoutubeDL(opts) as ydl:

    info = ydl.extract_info(
        url,
        download=False
    )

    output = {
        "video_id":
            video_id,

        "automatic_captions":
            list(
                (
                    info.get(
                        "automatic_captions"
                    )
                    or
                    {}
                ).keys()
            ),

        "subtitles":
            list(
                (
                    info.get(
                        "subtitles"
                    )
                    or
                    {}
                ).keys()
            )
    }

print(
    json.dumps(
        output,
        indent=2
    )
)
