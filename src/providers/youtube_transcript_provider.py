from youtube_transcript_api import (
    YouTubeTranscriptApi
)

from src.providers.transcript_provider import (
    TranscriptProvider
)

class YoutubeTranscriptProvider(
    TranscriptProvider
):

    def fetch(
        self,
        video_id
    ):

        api = (
            YouTubeTranscriptApi()
        )

        return api.fetch(
            video_id
        ).to_raw_data()
