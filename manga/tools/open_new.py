from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import Future
from typing import Callable, Dict, List, Set, Any
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


######################################################################
#                         Threading Handlers                         #
######################################################################


class ThreadHandler(ThreadPoolExecutor):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.futures: List[Future] = []
    def add(self, fn, *args: Any, **kwargs: Any) -> None:
        self.futures.append(super().submit(fn, *args, **kwargs))
    def kill(self):
        self.shutdown(wait=False)
        for i in self.futures:
            i.cancel()


mk_open_remaining_first: bool = True


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


def evaluate(url: str, tested: Dict[str, Set[str]], pbar: tqdm.std.tqdm) -> None:
    """
    Determine if url has a new chapter or not
    Store the result in tested and update pbar
    """
    try:
        tested["open" if sites.test(url) else "ignore"].add(url)
    except sites.UnknownDomain:
        tested["unknown"].add(url)
    except requests.exceptions.RequestException:
        tested["failed"].add(url)
    finally:
        pbar.update()


def handle_results(urls: Set[str], tested: Dict[str, Set[str]]) -> None:
    """
    Print out the test results and open each of the given URLs that should not be ignored
    """
    if len(tested["unknown"]) > 0:
        print("The following domains were not known:")
        print("\t" + "\n\t".join(sorted(tested["unknown"])))
    if len(tested["failed"]) > 0:
        print("The following domains could not be opened:")
        print("\t" + "\n\t".join(sorted(tested["failed"])))
    all_tested = set().union(*[ k for _, k in tested.items() ])
    if len(all_tested) != len(urls):
        print("The following domains were not tested:")
        print("\t" + "\n\t".join(sorted(urls - all_tested)))
        print("Assuming all remaining URLs must be opened...")
    print("Opening manga...")
    for url in tqdm.tqdm(urls - tested["ignore"]):
        subprocess.check_call(["open", url], stdout=subprocess.DEVNULL,)
        time.sleep(.2)  # Don't kill the machine


def open_new(directory: Path) -> bool:
    """
    Open each file in directory that has a new chapter ready
    """
    print("Checking arguments...")
    directory = directory.resolve()
    assert directory.exists(), f"{directory} does not exist"
    assert directory.is_dir(), f"{directory} is not a directory"
    # Determine which requests must be made
    print("Scanning files...")
    urls: Set[str] = { extract_url(i) for i in lsf(directory) }
    tested: Dict[str, Set[str]] = {
        "open" : set(),
        "ignore" : set(),
        "failed" : set(),
        "unknown" : set(),
    }
    # Determine what to open
    print(f"Making at most {len(urls)} requests...")
    original_sigint_handler: Any = signal.getsignal(signal.SIGINT)
    with tqdm.tqdm(total=len(urls)) as pbar:
        with ThreadHandler(max_workers=32) as executor: # No DDOS-ing
            signal.signal(signal.SIGINT, mk_open_remaining(executor, urls, tested))
            for i in urls:
                executor.add(evaluate, i, tested, pbar)
    signal.signal(signal.SIGINT, original_sigint_handler)
    # Open links
    handle_results(urls, tested)
    return True


def main(prog: str, *args: str) -> bool:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser(prog=os.path.basename(prog))
    parser.add_argument("directory", type=Path, help="The directory to open new items from")
    return open_new(**vars(parser.parse_args(args)))


def cli() -> None:
    sys.exit(0 if main(*sys.argv) else -1)
