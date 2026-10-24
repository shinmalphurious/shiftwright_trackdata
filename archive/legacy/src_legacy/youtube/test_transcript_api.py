from youtube_transcript_api import YouTubeTranscriptApi

api = YouTubeTranscriptApi()

video_id = "J3w5NMXyxcI"

try:

    transcript = api.fetch(video_id)

    print(
        "SUCCESS",
        len(transcript)
    )

    print(
        transcript[0]
    )

except Exception as e:

    print(type(e).__name__)
    print(e)
