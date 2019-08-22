import hashlib
import logging
import mimetypes
from abc import ABC, abstractmethod

from urllib3.util import parse_url

_log = logging.getLogger(__name__)


class ResourceURL:
    """
    An object that parses url using urllib3.util.parse_url and defines a
    resource by its location, schema and mimetype.

    Args:
        url (str): String represeting URL specified in RFC 1738.
        mimetype (str, optional): MIME type conforming definions in RFC 2045,
            RFC 2046, RFC 2047, RFC 4288, RFC 4289 and RFC 2049. Allow
            additional non-standard "text/yaml" mimetype for ".yaml" and ".yml"
            extensions. Override extracted mimetype from url if specified.
            Defaults to None.
    """
    def __init__(self, url, mimetype=None):
        self.raw_url = url
        self.url = parse_url(url)
        self.path = self.url.path

        # if url.scheme is None: set scheme to "file"
        self.scheme = self.url.scheme or "file"

        # specify mimetype from argument or read from url extension
        self.mimetype = mimetype or mimetypes.guess_type(url)[0]


class Reader(ABC):
    def __init__(self, url):
        """
        Wrap ResourceURL in a way that provides an interface to open resource,
        read through it and also calculate the hash sum without opening the
        file.

        Args:
            url (ResourceURL): resource URI representing mimetype, scheme and
                location of the resource.
        """
        self.url = url
        self.mimetype = url.mimetype
        self.path = url.path

    @abstractmethod
    def open(*args, **kwargs):
        pass

    @abstractmethod
    def hash(self):
        pass


class LocalFile(Reader):
    def __init__(self, url):
        """
        Read data and calculate sha256sum for a resource from local storage.

        Args:
            url (ResourceURL): resource URI representing mimetype, scheme and
                location of the resource.

        Raises:
            AssertionError: If ResourceURL.scheme is not `file` the resource is
                not a local file.
        """
        assert url.scheme is "file"
        super().__init__(url)

    def open(self, *args, **kwargs):
        """
        Method with arguments compatible with open() with `file=self.path`.
        For more details check out

                https://docs.python.org/3/library/functions.html#open
        """
        return open(self.path, *args, **kwargs)

    def hash(self):
        """
        Calculate sha256sum of a local file.

        Returns:
            str: sha256sum for file located on `self.path`
        """
        _log.debug(f"Started calculating sha256sum for '{self.path}'",
                   extra={"path": self.path})
        h = hashlib.sha256()
        b = bytearray(128 * 1024)
        mv = memoryview(b)
        with open(self.path, 'rb', buffering=0) as f:
            for n in iter(lambda: f.readinto(mv), 0):
                h.update(mv[:n])

        sha256sum = h.hexdigest()
        _log.debug(f"Finished calculating sha256sum for '{self.path}'",
                   extra={"path": self.path, "sha256sum": sha256sum})
        return sha256sum


# a simple list of supported resource readers
readers = [LocalFile]
