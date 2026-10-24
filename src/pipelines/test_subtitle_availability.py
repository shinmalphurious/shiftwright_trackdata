import yt_dlp

video_id = "1Za5r0B4YvE"

url = f"https://www.youtube.com/watch?v={video_id}"

opts = {
    "skip_download": True,
    "writesubtitles": True,
    "writeautomaticsub": True,
    "quiet": True
}

with yt_dlp.YoutubeDL(opts) as ydl:

    info = ydl.extract_info(
        url,
        download=False
    )

    print(
        "subtitles:",
        bool(
            info.get("subtitles")
        )
    )

    print(
        "automatic_captions:",
        bool(
            info.get("automatic_captions")
        )
    )
