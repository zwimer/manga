from __future__ import annotations
from concurrent.futures import Future, thread
from collections import defaultdict
from typing import TYPE_CHECKING
from functools import lru_cache
from pathlib import Path
import subprocess
import traceback
import argparse
import platform
import termios
import time
import sys

from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn, TaskProgressColumn
from tqdm import tqdm
import requests

from manga.utils import extract_url, lsf, split_on_num
from manga import sites

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


class ThreadHandler(thread.ThreadPoolExecutor):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.futures: list[Future] = []

    def add(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.futures.append(super().submit(fn, *args, **kwargs))

    def kill(self):
        self.shutdown(wait=False)
        for i in self.futures:
            i.cancel()


#
# Failure Classes
#


class Failed:
    reason: str = ""  # Set by subclasses
    _unique_reason: bool = False  # Overridden by subclasses if desired

    def __init__(self, url: str):
        self.url: str = url

    def __str__(self):
        if self._unique_reason:
            return f"{self.reason}: {self.url}"
        return self.url

    def __repr__(self):
        ret = f"<{self.__class__.__name__}: url='{self.url}'"
        if self._unique_reason:
            ret += f", reason='{self.reason}'"
        return ret + ">"

    @classmethod
    def kind(cls):
        if cls._unique_reason:
            return cls.__name__
        return f"{cls.__name__}: {cls.reason}"


# Should not happen


class NoOpen(Failed):
    pass


class Skipped(NoOpen):
    reason = "This domain was skipped"


class Unknown(NoOpen):
    reason = "This website is for an unknown / unsupported domain."


class BadRequest(NoOpen):
    _unique_reason = True

    def __init__(self, url: str, reason):
        super().__init__(url)
        self.reason = f"A request failed: {reason}"


class MalformedURL(NoOpen):
    pass


class NotInt(MalformedURL):
    reason = "The URL's chapter is not an integer."


class HasVol(MalformedURL):
    reason = "The URL contains 'vol'; this is a bad sign"


class Pattern(MalformedURL):
    reason = "The URL contains a pattern that is dangerous"


# Non-Malformed URL Failure Classes


class ToOpen(Failed):
    pass


class Tiny(ToOpen):
    reason = "URL failed by default, it is too small"


class Exists(ToOpen):
    reason = "The URL is valid, but this site seems to be missing other chapters"


class Missing(ToOpen):
    reason = "Previous and future chapters exist, this one does not."


class Broken(ToOpen):
    reason = "This website does not seem to have any chapters of this manga."


######################################################################
#                           Main Functions                           #
######################################################################


@lru_cache(maxsize=None)
def _test_site(url: str):
    return sites.test(url, timeout_retries=5)


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
def _evaluate(url: str) -> Failed | None:
    """
    If url is broken, return a failure class for it
    """
    if "vol" in url.lower():
        return HasVol(url)
    left, n, right = split_on_num(url)
    if n != int(n):
        return NotInt(url)
    elif n <= 5:
        return Tiny(url)
    elif "mangabuddy" in left and ("/mbx" in left or any(i.isalpha() for i in right)):
        return Pattern(url)
    test = lambda x: _test(left, right, x)
    try:
        if test(n) and not test(n - 1) and not test(5):
            return Exists(url)
        time.sleep(0.05)  # No DOS-ing
        if not test(n):
            for i in (0.1, 1, 1.1, 2, 2.1, 5, 10, 20):
                if test(n + i):
                    return Missing(url)
        time.sleep(0.1)  # No DOS-ing
        if not any(test(i) for i in (n, n - 1, 5, n + 0.1, n + 1, n + 1.1)):
            return Broken(url)
        time.sleep(0.05)  # No DOS-ing
        return None
    except sites.UnknownDomain:
        return Unknown(url)
    except requests.exceptions.RequestException as e:
        print(e)
        return BadRequest(url, e)


def evaluate(urls: str, delay: int, ret: list, pbar: Progress) -> None:
    """
    Determine if url is broken
    Store return value in ret because we the return value will be ignored
    """
    try:
        domain = sites.get_domain(urls[0])
        task = pbar.add_task(f"{domain}:", total=len(urls))
        update = lambda: pbar.update(task, advance=1)
        first: bool = False
        for i in urls:
            if not first:
                time.sleep(delay)
                first = False
            rv: Failed | None = _evaluate(i)
            if rv is not None:
                ret.append(rv)
            update()
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc()
        raise


def print_each(prefix: str, lst: list[Failed]):
    """
    Print every item in lst
    """
    if lst:
        lst = sorted(lst, key=lambda x: x.url)
        print(f"{prefix}\n\t" + "\n\t".join(str(i) for i in lst))


def open_each(opener: str, prefix: str, lst: list[Failed]) -> None:
    """
    Open every item in lst
    """
    if lst:
        print(f"{prefix}\n\t" + "\n\t".join(i.url for i in lst))
        for i in tqdm(lst, dynamic_ncols=True, leave=False):
            subprocess.check_call([opener, i.url], stdout=subprocess.DEVNULL)
        print("")


def test_sites(directory: Path, skip: set[str] | list[str], opener: str, no_prompt: bool, delay: int) -> bool:
    """
    Test each file in directory, print the results open them as needed
    """
    if isinstance(skip, list):
        return test_sites(directory, set(skip), opener, no_prompt, delay)
    print("Checking arguments...")
    directory = directory.resolve()
    assert delay >= 0, "Delay may not be negative"
    assert directory.exists(), f"{directory} does not exist"
    assert directory.is_dir(), f"{directory} is not a directory"
    # Determine which requests must be made
    print("Scanning files...")
    urls: set[str] = {extract_url(i) for i in lsf(directory)}
    # Bucket URLs
    bucketed = defaultdict(list)
    for i in urls:
        bucketed[sites.get_domain(i)].append(i)
    # Determine what to open
    tested: list[Failed] = []
    print(f"Testing {len(urls)} urls...")
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        TaskProgressColumn(),
        BarColumn(None),
        MofNCompleteColumn(),
        TimeRemainingColumn(compact=True, elapsed_when_finished=True),
        transient=True,
        expand=True,
    ) as pbar:
        for i in skip:
            got: list | None = bucketed.pop(i, None)
            if got is not None:
                pbar.add_task(i, total=len(got))
                for i in got:
                    tested.append(Skipped(i))
                pbar.update(i, advance=len(got))
        with ThreadHandler(max_workers=len(bucketed)) as executor:  # No DOS-ing
            for k in bucketed.values():
                executor.add(evaluate, k, delay, tested, pbar)
    # Results
    no_open: list[Failed] = [i for i in tested if isinstance(i, NoOpen)]
    to_open: list[Failed] = [i for i in tested if isinstance(i, ToOpen)]
    # Print no-open failures
    sub_list: Callable[[list[Failed], type], list[Failed]] = lambda lst, t: [i for i in lst if isinstance(i, t)]
    if no_open:
        print(f"{'*'*70}\n*{'Errors'.center(68)}*\n{'*'*70}\n")
        for sub in {i.__class__ for i in no_open}:
            print_each(sub.kind(), sub_list(no_open, sub))
        print(f"\n{'*'*70}\n*{'Done'.center(68)}*\n{'*'*70}\n")
    # Open
    if not no_prompt:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        _ = input("Testing complete. Hit enter to open websites.")
    for sub in {i.__class__ for i in to_open}:
        open_each(opener, sub.kind(), sub_list(to_open, sub))
    print("Done!")
    return True


def main(prog: str, *args: str) -> bool:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser(prog=Path(prog).name)
    parser.add_argument("directory", type=Path, help="The directory to test")
    parser.add_argument("--skip", type=str, nargs="+", default=[], help="Domains to skip")
    parser.add_argument("--opener", default="open", help="The default binary to open a URL with")
    parser.add_argument("--no-prompt", action="store_true", help="Auto open sites when complete, do not prompt user")
    parser.add_argument(
        "--delay",
        default=0,
        type=int,
        help="The number of seconds each thread should wait between testing sites (to avoid DOSing)",
    )
    return test_sites(**vars(parser.parse_args(args)))


def cli() -> None:
    sys.exit(0 if main(*sys.argv) else -1)
