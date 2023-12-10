from __future__ import annotations
from dataclasses import dataclass, astuple, field
from concurrent.futures import Future, thread
from typing import Callable, Any
from pathlib import Path
import subprocess
import argparse
import platform
import signal
import time
import sys
import os

import requests
import tqdm

from manga.utils import extract_url, lsf
from manga import sites


mk_open_remaining_first: bool = True


@dataclass
class Tested:
    """
    The results of testing every URL
    """

    has_new: set[str] = field(default_factory=set)
    ignore: set[str] = field(default_factory=set)
    skip: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)
    unknown: set[str] = field(default_factory=set)


######################################################################
#                         Threading Handlers                         #
######################################################################


class ThreadHandler(thread.ThreadPoolExecutor):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.futures: list[Future] = []

    def add(self, fn, *args: Any, **kwargs: Any) -> None:
        self.futures.append(super().submit(fn, *args, **kwargs))

    def kill(self):
        self.shutdown(wait=False)
        for i in self.futures:
            i.cancel()


def mk_open_remaining(executor, urls, tested) -> Callable[[int, Any], None]:
    """
    Return a signal handler to open the remaining tested URLs
    """

    def handler(_: int, _2: Any) -> None:
        global mk_open_remaining_first  # pylint: disable=global-statement
        if not mk_open_remaining_first:
            os._exit(1)  # pylint: disable=protected-access
        mk_open_remaining_first = False
        print("Terminating executor...")
        executor.kill()
        handle_results(urls, tested)
        os._exit(0)  # pylint: disable=protected-access

    return handler


######################################################################
#                           Main Functions                           #
######################################################################


def evaluate(url: str, tested: Tested, pbar: tqdm.std.tqdm) -> None:
    """
    Determine if url has a new chapter or not
    Store the result in tested and update pbar
    """
    try:
        (tested.has_new if sites.test(url) else tested.ignore).add(url)
    except sites.UnknownDomain:
        tested.unknown.add(url)
    except requests.exceptions.RequestException:
        tested.failed.add(url)
    finally:
        pbar.update()


def handle_results(urls: set[str], tested: Tested) -> None:
    """
    Print out the test results and open each of the given URLs that should not be ignored
    """
    if len(tested.unknown) > 0:
        print("The following domains were not known:")
        print("\t" + "\n\t".join(sorted(tested.unknown)))
    if len(tested.failed) > 0:
        print("The following domains could not be opened:")
        print("\t" + "\n\t".join(sorted(tested.failed)))
    if len(tested.skip) > 0:
        print("The following domains were skipped:")
        print("\t" + "\n\t".join(sorted(tested.skip)))
    all_tested = set().union(*astuple(tested))
    if len(all_tested) != len(urls):
        print("The following domains were not tested:")
        print("\t" + "\n\t".join(sorted(urls - all_tested)))
        print("Assuming all remaining URLs must be opened...")
    print("Opening manga...")
    for url in tqdm.tqdm(urls - tested.ignore - tested.skip):
        subprocess.check_call(["open", url], stdout=subprocess.DEVNULL)
        time.sleep(0.2)  # Rate limit


def open_new(directory: Path, skip: set[str] | list[str]) -> bool:
    """
    Open each file in directory that has a new chapter ready
    """
    if isinstance(skip, list):
        return open_new(directory, set(skip))
    print("Checking arguments...")
    directory = directory.resolve()
    assert directory.exists(), f"{directory} does not exist"
    assert directory.is_dir(), f"{directory} is not a directory"
    # Determine which requests must be made
    print("Scanning files...")
    urls: set[str] = {extract_url(i) for i in lsf(directory)}
    results = Tested()
    # Determine what to open
    print(f"Making at most {len(urls)} requests...")
    original_sigint_handler: Any = signal.getsignal(signal.SIGINT)
    with tqdm.tqdm(total=len(urls)) as pbar:
        with ThreadHandler(max_workers=32) as executor:  # No DOS-ing
            signal.signal(signal.SIGINT, mk_open_remaining(executor, urls, results))
            for i in urls:
                if sites.get_domain(i) in skip:
                    results.skip.add(i)
                    pbar.update()
                else:
                    executor.add(evaluate, i, results, pbar)
    signal.signal(signal.SIGINT, original_sigint_handler)
    # Open links
    handle_results(urls, results)
    return True


def main(prog: str, *args: str) -> bool:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser(prog=Path(prog).name)
    parser.add_argument("--skip", type=str, nargs="+", default=[], help="Domains to skip")
    parser.add_argument("directory", type=Path, help="The directory to open new items from")
    return open_new(**vars(parser.parse_args(args)))


def cli() -> None:
    sys.exit(0 if main(*sys.argv) else -1)
