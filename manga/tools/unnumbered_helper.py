from __future__ import annotations
from pathlib import Path
import collections
import argparse
import platform
import time

import osascript
import argcomplete

from manga.utils import split_on_num, extract_url, lsf, get_logger


def scrub(url: str) -> str:
    """
    Scrub a URL for easy comparison with others
    """
    url = "".join(url.split("//")[1:])
    if "." in url[:4]:
        url = url.split(".", 1)[1]
    if url.endswith("/"):
        url = url[:-1]
    if "?" in url:
        url = url.split("?", 1)[0]
    return url


def read_dir(directory: Path) -> dict[str, str]:
    """
    Read a directory and map the scrubbed URLs to their chapter numbers a strings
    Ignores .swp files but whines about them
    """
    assert directory.is_dir(), f"{directory} is a file"
    files: tuple[Path, ...] = lsf(directory)
    ret: dict[str, str] = {}
    for f in files:
        fname: str = f.name
        if fname.startswith(".") and f.suffix == ".swp":
            print(f"Refusing to open swap file: {f}")
            continue
        _, num, _2 = split_on_num(fname)
        ret[scrub(extract_url(f))] = str(num)
    return ret


def get_url() -> str:
    """
    Get the URL of the current tab
    """
    cmd: str = 'tell application "Google Chrome" to return URL of active tab of front window'
    code, out, err = osascript.run(cmd)
    assert code == 0, err
    return out


def unnumbered_helper(dirs: list[Path]) -> None:
    """
    Print out the number of the chapter associated
    with the manga displayed in the frontmost Chrome tab
    """
    for i in dirs:
        assert i.exists(), f"{i} does not exist"
    get_logger(__name__).info("Running on dirs: %s", dirs)
    raw_data: list[dict[str, str]] = [read_dir(i) for i in dirs]
    data: dict[str, str] = dict(collections.ChainMap(*raw_data))
    old: str | None = None
    while True:
        time.sleep(0.05)
        url: str = scrub(get_url())
        if url == old:
            continue
        old = url
        try:
            print(data[url])
        except KeyError:
            print("Unknown")


def cli() -> None:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", type=Path, nargs="+", help="The unnumbered directories")
    argcomplete.autocomplete(parser)  # Tab completion
    try:
        unnumbered_helper(**vars(parser.parse_args()))
    except KeyboardInterrupt:
        pass
