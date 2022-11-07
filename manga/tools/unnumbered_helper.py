from typing import Optional, Tuple, Dict, List
from pathlib import Path
import collections
import argparse
import platform
import time
import sys
import os

import osascript

from manga.utils import split_on_num, extract_url, lsf


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


def read_dir(directory: Path) -> Dict[str, str]:
    """
    Read a directory and map the scrubbed URLs to their chapter numbers a strings
    Ignores .swp files but whines about them
    """
    assert directory.is_dir(), f"{directory} is a file"
    files: Tuple[Path] = lsf(directory)
    ret: Dict[str, str] = {}
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


def unnumbered_helper(dirs: List[Path]) -> None:
    """
    Print out the number of the chapter associated
    with the manga displayed in the frontmost Chrome tab
    """
    for i in dirs:
        assert i.exists(), f"{i} does not exist"
    raw_data: List[Dict[str, str]] = [ read_dir(i) for i in dirs ]
    data: Dict[str, str] = dict(collections.ChainMap(*raw_data))
    old: Optional[str] = None
    while True:
        time.sleep(.05)
        url: str = scrub(get_url())
        if url == old:
            continue
        old = url
        try:
            print(data[url])
        except KeyError:
            print("Unknown")


def main(prog: str, *argv: str) -> bool:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser(prog=os.path.basename(prog))
    parser.add_argument("dirs", type=Path, nargs="+", help="The unnumbered directories")
    try:
        unnumbered_helper(**vars(parser.parse_args(argv)))
    except KeyboardInterrupt:
        pass
    return True


def cli() -> None:
    sys.exit(0 if main(*sys.argv) else -1)
