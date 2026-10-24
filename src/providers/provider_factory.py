from src.providers.youtube_transcript_provider import (
    YoutubeTranscriptProvider
)

from src.providers.ytdlp_caption_provider import (
    YtDlpCaptionProvider
)

def get_provider(
    name
):

    if name == "youtube":

        return (
            YoutubeTranscriptProvider()
        )

    if name == "ytdlp":

        return (
            YtDlpCaptionProvider()
        )

    raise ValueError(
        name
    )
