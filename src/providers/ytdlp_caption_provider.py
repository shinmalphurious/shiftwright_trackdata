import yt_dlp

from src.providers.transcript_provider import (
    TranscriptProvider
)

class YtDlpCaptionProvider(
    TranscriptProvider
):

    def fetch(
        self,
        video_id
    ):

        raise NotImplementedError(
            "caption download not yet implemented"
        )
