import logging
import time

from useful.resource.readers import ResourceURL, readers
from useful.resource.parsers import parsers

_log = logging.getLogger(__name__)


def _get(registry, default=None, **kwargs):
    """
    Get default value or instance created with **kwargs. Applies to both
    readers and parsers, if creating an instance by calling obj(**kwargs) does
    not raise AssertionError, we found a Reader or Parser that supports given
    scheme or mimetype, respectively.

    Args:
        registry (list): A list of classes.
        default (obj, optional): A default class allowing user to override the
            available choices from the provided registry list. Defaults to
            None.

    Returns:
        obj: Selected instance created by providing **kwargs.
    """
    if default is not None:
        _log.debug(f"Using {default.__name__}",
                   extra={"class": default.__name__})
        return default(**kwargs)
    else:
        for obj in registry:
            try:
                instance = obj(**kwargs)
                _log.debug(f"Using {obj.__name__}",
                           extra={"class": obj.__name__})
                return instance
            except AssertionError:
                pass

    _log.debug("Using 'None'", extra={"class": None})
    return None


def cached_load(timeout=300):
    """
    Define timeout to be used in `load()` function.


    Args:
        timeout (int, optional): Number of seconds to cache data without
            checking if it has changed in any way. Defaults to 300.

    Returns:
        function: A function using timeout variable
    """
    memory = {}

    def load(url, mimetype=None, parser=None, handler=None):
        """
        Load resource from uri or cache if already used before.

        Args:
            url (str): String represeting URL specified in RFC 1738.
            mimetype (str, optional): Forced MIME type if not None. Defaults to
                None.
            parser (useful.resource.parsers.Parser, optional): A parser class
                to use instead of parsers from useful.resource.parsers.parsers.
                Defaults to None.
            handler (callable, optional): An optional function to call after
                reading and parsing the data. Defaults to None.

        Raises:
            ValueError: No reader supports provided url scheme
            ValueError: No parser supports provided mimetype

        Returns:
            [type]: [description]
        """
        hash_ = None

        # get the reader from url
        resource_url = ResourceURL(url, mimetype=mimetype)
        reader = _get(registry=readers, url=resource_url)
        if reader is None:
            raise ValueError(
                f"Unsupported reader scheme '{resource_url.scheme}'")

        # if url has been cached for less than `timeout` or hash sum of the
        # resource is still equal, return cached value
        if url in memory:
            if time.time() - memory[url]['time'] < timeout:
                _log.debug(
                    f"Url '{url}' in memory for less then {timeout} seconds",
                    extra={"url": url, "timeout": timeout})    
                return memory[url]['data']
            else:
                hash_ = reader.hash()
                if hash_ == memory[url]['hash']:
                    _log.debug(
                        f"Url '{url}' in memory hasn't changed hash sum",
                        extra={"url": url, "hash": hash_})
                    return memory[url]['data']

        # if url has been cached but needs to update use caches handler as a
        # handler, otherwise use function parameter handler as handler object
        handler = memory.get(url, {}).get("handler", handler)
        # use already calculated above hash sum or calculate hash sum if it was
        # never calculated
        hash_ = hash_ or reader.hash()

        # get reader parser
        parser = _get(registry=parsers, default=parser, reader=reader)
        if parser is None:
            raise ValueError("Unsupported parser")

        # parse reader
        data = parser()

        # call handler on data
        if handler is not None:
            data = handler(data)

        # cache results and other relevant data
        memory[url] = {
            'time': time.time(),
            'hash': hash_,
            'data': data,
            'handler': handler
        }
        _log.debug(f"Upserting url '{url}' in memory",
                   extra={"url": url, "hash": hash_})
        return data

    return load


load = cached_load(timeout=300)
