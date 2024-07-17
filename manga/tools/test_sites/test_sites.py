from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
from time import sleep
import traceback

from manga.utils import extract_url, lsf

from .test_url import test_url
from .dispatch import dispatch
from .state import State, URL
from .status import Skipped
from .results import results

if TYPE_CHECKING:
    from collections.abc import Callable


_skipped = Skipped()


def evaluate_urls(urls: list[URL], update_pbar: Callable[[], None], skip: set[str], delay: int) -> None:
    """
    :param urls: The list of URLs to test
    :param update_pbar: A function that updates the progress bar to be called when a URL is tested
    :param skip: A set of domains to skip
    :param delay: How many seconds to sleep before testing successive urls
    """
    try:
        if urls[0].domain in skip:
            for i in urls:
                i.status = _skipped
                update_pbar()
            return
        first: bool = False
        for url in urls:
            if not first:
                sleep(delay)
                first = False
            url.status = test_url(url.url)
            update_pbar()
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc()
        raise


def test_sites(
    directory: Path,
    skip: set[str] | list[str],
    opener: str,
    skip_tiny: bool,
    skip_point_five: bool,
    no_prompt: bool,
    delay: int,
) -> bool:
    """
    Test each file in directory, print the results open them as needed
    """
    if isinstance(skip, list):
        return test_sites(directory, set(skip), opener, skip_tiny, skip_point_five, no_prompt, delay)
    print("Checking arguments...")
    directory = directory.resolve()
    assert delay >= 0, "Delay may not be negative"
    assert directory.exists(), f"{directory} does not exist"
    assert directory.is_dir(), f"{directory} is not a directory"
    # Test
    print("Scanning files...")
    state = State({extract_url(i) for i in lsf(directory)})
    print(f"Testing {len(state)} urls...")
    dispatch(state, evaluate_urls, skip, delay)
    # Results
    results(state, no_prompt, skip_tiny, skip_point_five, opener)
    return True
