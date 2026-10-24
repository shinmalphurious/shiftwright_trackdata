import yt_dlp

with yt_dlp.YoutubeDL(
    {
        "quiet": True,
        "js_runtimes": {
            "node": {}
        }
    }
) as ydl:

    print(
        "yt-dlp started"
    )
