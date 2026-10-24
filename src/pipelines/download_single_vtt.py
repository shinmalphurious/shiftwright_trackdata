import yt_dlp

video_id = "1Za5r0B4YvE"

url = f"https://www.youtube.com/watch?v={video_id}"

opts = {
    "skip_download": True,

    "writesubtitles": False,

    "writeautomaticsub": True,

    "subtitleslangs": ["en"],

    "subtitlesformat": "vtt",

    "sleep_interval_requests": 5,

    "extractor_retries": 0,

    "outtmpl": "research/youtube/transcripts/%(id)s"
}

with yt_dlp.YoutubeDL(opts) as ydl:

    ydl.download(
        [url]
    )

print(
    "caption_download_complete"
)
