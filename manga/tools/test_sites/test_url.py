from functools import cache
from time import sleep

import requests

from manga.utils import split_on_num
from manga import sites

from .status import (
    Success,
    Tested,
    HasVol,
    NotInt,
    Tiny,
    Pattern,
    Exists,
    Missing,
    Broken,
    Unknown,
    BadRequest,
    PointFive,
)


_success = Success()


@cache
def _test_site(url: str) -> bool:
    return sites.test(url, timeout_retries=8)


def _test(left: str, right: str, x: float) -> bool:
    """
    Test if chapter x is found at a URL constructed from left, right, and x
    """
    if int(x) == x:
        return _test_site(f"{left}{int(x)}{right}")
    else:
        if _test_site(f"{left}{x}{right}"):
            return True
        return _test_site(f"{left}{str(x).replace('.', '-')}{right}")


# pylint: disable=too-many-return-statements,too-many-branches
def test_url(url: str) -> Tested:
    """
    If url is broken, return a failure class for it
    """
    if "vol" in url.lower():
        return HasVol()
    left, n, right = split_on_num(url)
    if n != int(n):
        return NotInt()
    elif n <= 5:
        return Tiny()
    elif "mangabuddy" in left and ("/mbx" in left or any(i.isalpha() for i in right)):
        return Pattern()
    test = lambda x: _test(left, right, x)
    try:
        if test(n) and not test(n - 1) and not test(5):
            return Exists()
        sleep(0.04)  # No DOS-ing
        if not test(n):
            if any(test(n + i) for i in (0.1, 0.5, 1, 1.1, 2, 2.1, 5, 10, 20)):
                return Missing()
            sleep(0.08)  # No DOS-ing
            if test(n - 0.5):
                return PointFive()
        sleep(0.01)  # No DOS-ing
        if not any(test(i) for i in (n, n - 1, 5, n + 0.1, n + 0.5, n - 0.5, n + 1, n + 1.1, n + 5)):
            return Broken()
        sleep(0.04)  # No DOS-ing
        return _success
    except sites.UnknownDomain:
        return Unknown()
    except requests.exceptions.RequestException as e:
        print(e)
        return BadRequest(e)
