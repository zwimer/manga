from pathlib import Path
import platform
import argparse
import sys

from .open_new import open_new


def main(prog: str, *args: str) -> bool:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser(prog=Path(prog).name)
    parser.add_argument("--skip", type=str, nargs="+", default=[], help="Domains to skip")
    parser.add_argument("directory", type=Path, help="The directory to open new items from")
    return open_new(**vars(parser.parse_args(args)))


def cli() -> None:
    sys.exit(0 if main(*sys.argv) else -1)
