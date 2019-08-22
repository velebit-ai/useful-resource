from abc import ABC, abstractmethod
import json
import logging
import pickle
import mimetypes

import yaml

_log = logging.getLogger(__name__)


class Parser(ABC):
    def __init__(self, reader):
        """
        Abstract Parser class providing the parser interface, a single
        Parser.__call__() method.

        Args:
            reader (useful.resource.Reader): A Reader instance
                to use for reading data when parsing.
        """
        self.reader = reader

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


def _call_helper(reader, parse_method):
    """
    Read through resource and call parse_method on the file object.

    Args:
        reader (useful.resource.Reader): Reader to use for getting the data.
        parse_method (function): function to call on file-like object provided
            by the Reader.open method.

    Returns:
        obj: Parsed data
    """
    with reader.open("rb") as f:
        _log.debug(f"Started reading '{reader.url.url}'",
                   extra={"url": reader.url.url})
        data = parse_method(f)
        _log.debug(f"Finished reading '{reader.url.url}'",
                   extra={"url": reader.url.url})
    return data


class JSON(Parser):
    def __init__(self, reader):
        """
        A class for parsing JSON resources.

        Args:
            reader (useful.resource.Reader): A Reader instance
                to use for reading data when parsing.

        Raises:
            AssertionError: If mimetype is not "application/json"
        """
        assert reader.mimetype == "application/json"
        super().__init__(reader)

    def __call__(self):
        return _call_helper(self.reader, json.load)


class YAML(Parser):
    def __init__(self, reader):
        """
        A class for parsing YAML resources.

        Args:
            reader (useful.resource.Reader): A Reader instance
                to use for reading data when parsing.

        Raises:
            AssertionError: If mimetype is not "application/yaml"
        """
        assert reader.mimetype == "application/yaml"
        super().__init__(reader)

    def __call__(self):
        return _call_helper(self.reader, yaml.safe_load)


class Pickle(Parser):
    def __init__(self, reader):
        """
        A class for parsing pickle resources.

        Args:
            reader (useful.resource.Reader): A Reader instance
                to use for reading data when parsing.

        Raises:
            AssertionError: If mimetype is not "application/pickle"
        """
        assert reader.mimetype == "application/pickle"
        super().__init__(reader)

    def __call__(self):
        return _call_helper(self.reader, pickle.load)


class Generic(Parser):
    def __call__(self):
        """
        A class for reading through data without parsing.

        Args:
            reader (useful.resource.Reader): A Reader instance
                to use for reading data when parsing.
        """
        return _call_helper(self.reader, lambda x: x.read())


# add custom yaml mime type
mimetypes.add_type("application/yaml", ".yaml")
mimetypes.add_type("application/yaml", ".yml")
# add custom pickle mime type
mimetypes.add_type("application/pickle", ".pkl")

# a simple list of supported reader parsers
parsers = [JSON, YAML, Pickle, Generic]
