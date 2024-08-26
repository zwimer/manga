from collections.abc import Callable
from random import choice
from time import sleep

import tldextract
import requests

from .unknown_domain import UnknownDomain
from .domains import domains


_agents = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0",
)


def get_domain(url: str) -> str:
    """
    Extract the domain portion of a URL
    """
    info: tldextract.tldextract.ExtractResult = tldextract.extract(url)
    return f"{info.domain}.{info.suffix}"


def _test(url: str, fn: Callable[[str], bool], timeout: float, timeout_retries: int, base_delay: float) -> bool:
    """
    Return true if the given chapter is found
    If a timeout occurs, retries at most timeout_retries times; sleeps in between
    """
    session = requests.Session()
    session.headers.update({"User-Agent": choice(_agents)})
    what: str
    try:
        response = session.get(url, timeout=timeout)
        if response.ok:
            return fn(response.text)
        if response.status_code == 404:
            return False
        if response.status_code not in (429, 503):
            print(f"Got {response.status_code} from GET {url}")
            return False
        what = f"Got {response.status_code}"
    except requests.exceptions.ReadTimeout:
        what = "ReadTimeout"
    # Timeout or too many requests error at this point
    if timeout_retries <= 0:
        raise RuntimeError(what)
    if base_delay > 60:
        print(f"{what} for: {url}: Sleeping for {base_delay} seconds then trying again")
    sleep(base_delay)
    return _test(url, fn, timeout, timeout_retries - 1, min(base_delay * 2, 960.0))


def test(url: str, timeout: float = 7.5, timeout_retries: int = 0, base_delay: float = 7.5) -> bool:
    """
    Return true if the given chapter is found
    If a timeout occurs, retries at most timeout_retries times; sleeps in between
    """
    domain: str = get_domain(url)
    try:
        fn: Callable[[str], bool] = domains[domain]
    except KeyError:
        raise UnknownDomain(url)  # pylint: disable=raise-missing-from
    return _test(url, fn, timeout, timeout_retries, base_delay)
