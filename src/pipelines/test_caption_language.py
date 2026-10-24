import yt_dlp

video_id = "1Za5r0B4YvE"

url = f"https://www.youtube.com/watch?v={video_id}"

opts = {
    "skip_download": True,
    "writeautomaticsub": True,
    "writesubtitles": True,
    "subtitleslangs": ["en"]
}

with yt_dlp.YoutubeDL(opts) as ydl:

    info = ydl.extract_info(
        url,
        download=False
    )

    auto = info.get(
        "automatic_captions",
        {}
    )

    print(
        "languages:"
    )

    print(
        sorted(auto.keys())
    )
