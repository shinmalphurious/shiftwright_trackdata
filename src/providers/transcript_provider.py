from abc import ABC,abstractmethod

class TranscriptProvider(
    ABC
):

    @abstractmethod
    def fetch(
        self,
        video_id
    ):
        pass
