from __future__ import annotations
from typing import TYPE_CHECKING
from signal import Signals
from pathlib import Path
import os

import requests
import tqdm

from manga.utils import redirect_print_to_tqdm, extract_url, lsf
from manga import sites

from .thread_handler import ThreadHandler
from .results import handle_results
from .tested import Tested

if TYPE_CHECKING:
    from typing import Any


mk_open_remaining_first: bool = True


def evaluate(url: str, tested: Tested, pbar: tqdm.std.tqdm) -> None:
    """
    Determine if url has a new chapter or not
    Store the result in tested and update pbar
    """
    try:
        status: bool = sites.test(url, timeout_retries=3, base_delay=30)
        (tested.has_new if status else tested.ignore).add(url)
    except sites.UnknownDomain:
        tested.unknown.add(url)
    except requests.exceptions.RequestException:
        tested.failed.add(url)
    except Exception as e:
        print(f"Thread failed: {e}")
    finally:
        pbar.update()


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

    # Sigint handler
    def sigint_handler(executor: ThreadHandler, *_: Any) -> None:
        global mk_open_remaining_first  # pylint: disable=global-statement
        if not mk_open_remaining_first:
            os._exit(1)  # pylint: disable=protected-access
        mk_open_remaining_first = False
        print("Terminating executor...")
        executor.kill()
        handle_results(urls, results)
        os._exit(0)  # pylint: disable=protected-access

    # Siginfo handler
    def siginfo_handler(executor: ThreadHandler, *_: Any) -> None:
        untested: set[str] = urls - results.tested
        if not untested:
            return
        print("Still untested:")
        for i in untested:
            print(i)

    # Determine what to open
    print(f"Making at most {len(urls)} requests...")
    with tqdm.tqdm(total=len(urls), dynamic_ncols=True) as pbar:
        with redirect_print_to_tqdm():
            with ThreadHandler(
                max_workers=32, handlers={Signals.SIGINT: sigint_handler, Signals.SIGINFO: siginfo_handler}
            ) as executor:
                for i in urls:
                    if sites.get_domain(i) in skip:
                        results.skip.add(i)
                        pbar.update()
                    else:
                        executor.add(evaluate, i, results, pbar)
    # Open links
    handle_results(urls, results)
    return True
