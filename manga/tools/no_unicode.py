from __future__ import annotations
from pathlib import Path
import argparse
import sys

from manga.utils import mv


swap: dict[str, str] = {
    "￣": "",
    "∇": "",
    "ゞ": "",
    "…": "...",
    "ō": "o",
    "’": '"',
    "–": "-",
    "【": "[",
    "】": "]",
    "“": '"',
    "”": '"',
    "〜": "~",
    "～": "~",
    "«": "<<",
    "»": ">>",
}


def replace_unicode(x: str) -> str:
    """
    Replace unicode in x
    """
    for i, k in swap.items():
        x = x.replace(i, k)
    return x


def no_unicode(paths: list[Path], dryrun: bool) -> bool:
    """
    Remove unicode in each path's name
    """
    for path in paths:
        path = path.absolute()
        assert path.exists(), f"{path} does not exist"
        new: Path = path.parent / replace_unicode(path.name)
        if path != new:
            mv(path, new, dryrun=dryrun)
    return True


def main(argv) -> bool:
    parser = argparse.ArgumentParser(prog=Path(argv[0]).name)
    parser.add_argument("-M", "--dryrun", action="store_true", default=False)
    parser.add_argument("paths", type=Path, nargs="+")
    return no_unicode(**vars(parser.parse_args(argv)))


def cli() -> None:
    sys.exit(0 if main(sys.argv) else -1)
