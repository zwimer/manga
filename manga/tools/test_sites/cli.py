from pathlib import Path
import argparse
import platform
import sys

from .test_sites import test_sites


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
