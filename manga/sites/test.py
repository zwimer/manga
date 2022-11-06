from .unknown_domain import UnknownDomain
from .domains import domains

from typing import Callable

import tldextract
import requests


def get_domain(url: str) -> str:
    """
    Extract the domain portion of a URL
    """
    info: str = tldextract.extract(url)
    return f"{info.domain}.{info.suffix}"


def test(url: str, timeout: int = 15) -> bool:
    """
    Return true if the given chapter is found
    """
    domain: str = get_domain(url)
    try:
        fn: Callable[[str], bool] = domains[domain]
    except KeyError:
        raise UnknownDomain(url)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4"
    })
    return fn(session.get(url, timeout=timeout).text)
