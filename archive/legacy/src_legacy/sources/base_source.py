class SourceAdapter:

    source_name = "base"

    def search(self, track_name):
        raise NotImplementedError

    def extract(self, url):
        raise NotImplementedError

    def normalize(self, data):
        raise NotImplementedError
