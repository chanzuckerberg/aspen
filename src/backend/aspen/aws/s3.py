from urllib.parse import urlparse


class S3UrlParser:
    def __init__(self, url):
        self._parts = urlparse(url)

    @property
    def bucket(self):
        return self._parts.netloc

    @property
    def key(self):
        return self._parts.path.lstrip("/")
