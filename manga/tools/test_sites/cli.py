from pathlib import Path
import argparse
import platform
import sys

import argcomplete

from manga.sites import domains
from .test_sites import test_sites


class Supported(argparse.Action):
    def __call__(self, _, _2, arg, _3):
        arg = ("" if arg is None else arg).split("//", 1)[-1].split("/")[0]
        match = tuple(i for i in domains if arg in i)
        print("No matches found." if len(match) == 0 else "\n".join(match))
        sys.exit(0)


def cli() -> None:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--supported",
        action=Supported,
        nargs="?",
        help="Show supported sites containign this string then exit. If no string is passed, show all supported sites",
    )
    parser.add_argument("directory", type=Path, help="The directory to test")
    parser.add_argument("--opener", default="open", help="The default binary to open a URL with")
    parser.add_argument("--no-prompt", action="store_true", help="Auto open sites when complete, do not prompt user")
    parser.add_argument(
        "--delay",
        default=0,
        type=int,
        help="The number of seconds each thread should wait between testing sites (to avoid DOSing)",
    )
    skip = parser.add_argument_group("Skip Options")
    skip.add_argument("--skip", type=str, nargs="+", default=[], help="Domains to skip")
    skip.add_argument(
        "--skip-tiny", action="store_true", help="Do not open sites that were not tested because of a low chapter count"
    )
    skip.add_argument(
        "--skip-point-five", action="store_true", help="Do not open sites have a .5 chapter after the latest chapter"
    )
    argcomplete.autocomplete(parser)  # Tab completion
    ns = parser.parse_args()
    del ns.supported
    sys.exit(0 if test_sites(**vars(ns)) else -1)
