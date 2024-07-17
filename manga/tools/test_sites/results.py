from __future__ import annotations
from typing import TYPE_CHECKING, cast
import subprocess
import termios
import sys

from tqdm import tqdm

from .status import NoOpen, ToOpen, Broken, Exists, Missing, Tiny, PointFive

if TYPE_CHECKING:
    from .state import State, URL


_order = (Broken, Exists, Missing, PointFive, Tiny)


def _fmt(x: URL) -> str:
    if (exc := getattr(x.status, "exc", None)) is not None:
        return f"{x.url}: {exc}"
    return x.url


def print_no_open_failures(state: State) -> None:
    no_open: tuple[URL, ...] = state.get(NoOpen)
    if no_open:
        print(f"{'*'*70}\n*{'Errors'.center(68)}*\n{'*'*70}\n")
        for type_ in {cast(NoOpen, i.status).__class__ for i in no_open}:  # Set de-dups
            got = sorted(state.get(type_), key=lambda x: x.url)
            print(f"{type_.kind()}\n\t" + "\n\t".join(_fmt(i) for i in got) + "\n")
        print(f"{'*' * 70}\n*{'Done'.center(68)}*\n{'*' * 70}\n")


def print_open_failures(state: State, no_prompt: bool, skip_tiny: bool, skip_point_five: bool, opener: str) -> None:
    to_open: tuple[URL, ...] = state.get(ToOpen)
    if not to_open:
        return
    if not no_prompt:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        _ = input("Testing complete. Hit enter to open websites.")
    classes = {cast(ToOpen, i.status).__class__ for i in to_open}  # Set de-dups
    for type_ in sorted(classes, key=lambda t: _order.index(t) if t in _order else len(_order)):
        if skip_tiny and type_ is Tiny:
            print("Skipping tiny\n")
            continue
        if skip_point_five and type_ is PointFive:
            print("Skipping .5\n")
            continue
        got = state.get(type_)
        print(f"{type_.kind()}\n\t" + "\n\t".join(_fmt(i) for i in got))
        for url in tqdm(got, dynamic_ncols=True, leave=False):
            subprocess.check_call([opener, url.url], stdout=subprocess.DEVNULL)
        print("")


def results(state: State, no_prompt: bool, skip_tiny: bool, skip_point_five: bool, opener: str) -> None:
    print_no_open_failures(state)
    print_open_failures(state, no_prompt, skip_tiny, skip_point_five, opener)
    print("Done!")
