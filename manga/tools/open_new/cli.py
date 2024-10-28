from pathlib import Path
import platform
import argparse
import sys

import argcomplete

from .open_new import open_new


def cli() -> None:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip", type=str, nargs="+", default=[], help="Domains to skip")
    parser.add_argument("directory", type=Path, help="The directory to open new items from")
    argcomplete.autocomplete(parser)  # Tab completion
    sys.exit(0 if open_new(**vars(parser.parse_args())) else -1)
