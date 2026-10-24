import yt_dlp
import urllib.request

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

    url = (
        info[
            "automatic_captions"
        ][
            "en"
        ][0][
            "url"
        ]
    )

    print(
        "testing..."
    )

    try:

        data = urllib.request.urlopen(
            url,
            timeout=15
        ).read(200)

        print(
            "SUCCESS"
        )

        print(
            data[:100]
        )

    except Exception as ex:

        print(
            "FAIL"
        )

        print(ex)
