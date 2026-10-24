import yt_dlp

query = "iRacing Zandvoort track guide"

opts = {
    "quiet": True,
    "extract_flat": True
}

with yt_dlp.YoutubeDL(
    opts
) as ydl:

    result = ydl.extract_info(
        f"ytsearch10:{query}",
        download=False
    )

for entry in result["entries"]:

    print(
        entry["id"],
        "|",
        entry["title"]
    )
