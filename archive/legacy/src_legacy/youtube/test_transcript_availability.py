from youtube_transcript_api import YouTubeTranscriptApi

VIDEOS = [
    "J3w5NMXyxcI",
    "Y2yHC90ePI8",
    "i7N7ylDPLYI",
    "OIJni8p34Pk",
    "PxqIbNPnSgQ"
]

for video_id in VIDEOS:

    try:

        transcript = YouTubeTranscriptApi.get_transcript(
            video_id
        )

        print(
            f"{video_id},YES,{len(transcript)}"
        )

    except Exception as e:

        print(
            f"{video_id},NO,{type(e).__name__}"
        )
