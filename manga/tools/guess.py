from __future__ import annotations
from collections.abc import Sequence, Callable
from pathlib import Path
from typing import Any
import collections
import platform
import argparse
import sys
import re

import argcomplete

from manga.utils import split_on_num, extract_url, lsf, mv


# Config
TOLERANCE: int = 20
TRASH: Path = Path.home() / ".Trash/guess-manga/"
MAX_CHAPTER: int = 2500  # Higher has an increased chance of error


######################################################################
#                                                                    #
#                           Read directory                           #
#                                                                    #
######################################################################


def read_dir(d: Path, *, remove_numbers: bool = False) -> dict[str, Path]:
    """
    Read the files in a directory
    Return a dict mapping the scrubbed URLs they contain to the files within
    Fails if two files contain the same URLs after scrubbing
    """
    files: tuple[Path, ...] = lsf(d)
    scrub_to_file: dict[str, list[Path]] = collections.defaultdict(list)
    for f in files:
        scb: str = scrub(extract_url(f), remove_numbers=remove_numbers)
        scrub_to_file[scb].append(f)
    duplicates: list[tuple[str, list[Path]]] = [(i, k) for i, k in scrub_to_file.items() if len(k) != 1]
    if len(duplicates) > 0:
        disp_warning(f"Warning: duplicated files in: {d}")
        print("\nIgnoring the following sets of files:")
        print(",\n".join((i + ": {\n\t" + ",\n\t".join(str(j) for j in k) + "\n") for i, k in duplicates))
    return {i: k[0] for i, k in scrub_to_file.items() if len(k) == 1}


######################################################################
#                                                                    #
#                             Link Guess                             #
#                                                                    #
######################################################################


def remove_unwanted_periods(x: str) -> str:
    """
    Remove periods that are not part of a number
    Numbers are assumed to start and end with a digit, not a decimal point
    """
    for offset, pat in enumerate((r"\.[^\d]", r"[^\d]\.")):
        res: re.Match | None = re.compile(pat).search(x)
        if res is not None:
            idx: int = offset + x.find(res.group())
            x = x[:idx] + x[idx + 1 :]
            return remove_unwanted_periods(x)
    while len(x) and x[0] == ".":
        x = x[1:]
    while len(x) and x[-1] == ".":
        x = x[:-1]
    return x


def scrub(x: str, *, remove_numbers: bool = False) -> str:
    """
    Scrub a URL clean of 'mucky' information that makes it hard to compare with others
    For example: remove 'www.' since not all URLs need this
    """
    # Trim
    x = x.split("?")[0]

    # Remove unimportant words
    x = x.lower()
    x = re.sub(r"http://ww\d*\.", "", x)
    x = re.sub(r"https://ww\d*\.", "", x)
    x = re.sub(r"http://www\d*\.", "", x)
    x = re.sub(r"https://www\d*\.", "", x)
    x = x.replace("https", "").replace("http", "").replace("www", "")

    # If remove numbers
    if remove_numbers:
        x = re.sub(r"\d", "", x)

    # Clean
    x = re.sub(r"[^a-z\. \d]", " ", x)
    x = remove_unwanted_periods(x)
    while "  " in x:
        x = x.replace("  ", " ")
    return x.strip()


def diff_helper(a: str, b: str) -> tuple[str, str]:
    """
    Return the substrings of a and b whose first character
    is the first character that differs between a and b
    """
    r: int = min(len(a), len(b))
    for i in range(r):
        if a[i] != b[i]:
            return a[i:], b[i:]
    return a[r:], b[r:]


def are_same(guessing: str, compare_to: str) -> bool:
    """
    Determine if guessing and compare_to link to the same manga, and that they link to chapters
    If they are both the same manga and same chapter, an exception is raised
    compare_to may not contain guessing, and guessing must contain a chapter!
    """
    assert guessing != compare_to, f"{guessing} already exists"
    # Ex. (ch 1.1 reverting to ch 1)
    assert compare_to not in guessing, f"{compare_to} contains the URL being guessed: {guessing}"
    # Remove identical components
    a, b = diff_helper(guessing, compare_to)
    a, b = diff_helper(a[::-1], b[::-1])
    # The only bit left should be the chapters
    weird: bool
    try:
        guessing_ch = float(a[::-1])
        weird = guessing_ch > MAX_CHAPTER
        if len(b):
            compare_to_ch = float(b[::-1])
            weird &= compare_to_ch > MAX_CHAPTER or guessing_ch > compare_to_ch
    except ValueError:  # The float conversion failed, links did not match
        return False
    if not weird:
        return True
    print(f"Sanity check failed:\n\tNew: {guessing}\n\tOld: {compare_to}\nAre these the same? [y/N]")
    return "y" == input()


def choose(x: Any, near: Sequence[Any]) -> Any | None:
    """
    Prompt the user to select the nearest element in near to x
    If near only has one option, that choice is selected automatically
    May return None if the user selects no option
    """
    if len(near) == 1:
        return near[0]
    print(f"What is nearest to: {x}")
    st: Callable[[int], str] = lambda x: f"{x}.".ljust(3) + " "
    for i, k in enumerate(near):
        print(f"\t{st(i)}{k}")
    print(f"\t{st(len(near))}None of the above")
    try:
        choice = int(input())
        assert 0 <= choice <= len(near), "Invalid choice."
        if choice == len(near):
            return None
        return near[choice]
    except (ValueError, AssertionError):
        return choose(x, near)


######################################################################
#                                                                    #
#                             Link Guess                             #
#                                                                    #
######################################################################


def disp_warning(x: str) -> None:
    """
    Print out a warning: x
    """
    warn: str = " WARNING "
    delim: str = "*" * max(18, round((8 + len(x) - len(warn)) / 2))
    boarder: str = delim + warn + delim
    blank: str = "*" + " " * (len(boarder) - 2) + "*"
    middle: str = "*" + x.center(len(boarder) - 2) + "*"
    print("\n".join((boarder, blank, middle, blank, boarder)))


# pylint: disable=too-many-locals
def guess_single(raw: Path, data: dict[str, Path], yes: bool, force: bool, dryrun: bool) -> bool:
    """
    Try to replace the file in old for the same manga with raw, editing the title as needed
    Return true on success
    """
    # Link match
    raw_data: str = extract_url(raw)
    scrubbed_data: str = scrub(raw_data)
    options: list[str] = [i for i in data.keys() if are_same(scrubbed_data, i)]
    assert len(options) > 0, "Link matching failed"
    if len(options) > 1 and yes:
        raise RuntimeError("User input requires but --yes given, failing")
    choice: str | None = choose(scrubbed_data, options)
    if choice is None:
        return False
    old: Path = data[choice]

    # Extract chapter numbers
    old_data: str = extract_url(old)
    _, old_n, _ = split_on_num(old_data)
    _, new_n, _ = split_on_num(raw_data)  # new chapter is raw's chapter

    # Construct new file's name
    old_base: str = old.name
    assert any(c.isdigit() for c in old_base), f"{old} has no chapter number in its name"
    left, _, right = split_on_num(old_base)
    assert (
        right.startswith(".") and right.count(".") == 1
    ), f"{old_base} should have a file extension with a single period in it right after the chapter number"
    new_base: str = left + str(int(new_n) if new_n == int(new_n) else new_n) + raw.suffix

    # Determine danger level
    diff: float = new_n - old_n
    serious_warn: bool = diff <= 0 or diff > TOLERANCE
    warn: bool = serious_warn or diff == 0 or diff > 3

    # Prompt user to accept unless not required
    accept: str
    print(f"\nRaw: {raw.name}\nNew: {new_base}")
    if serious_warn or warn:
        print(f"Old: {old_base}\n")
        diff_str = str(int(diff) if diff == int(diff) else diff)
        disp_warning(f"Chapter number difference of: {diff_str}")
    print("")
    if not yes:
        print("Accept? [N/?/y]")
        accept = input()
    elif force and serious_warn:
        print("Serious warning detected, overriding forced. Failing...")
        accept = "N"
    elif force or not warn:
        print("Auto accepting.")
        accept = "y"

    # Act on prompt input
    if accept == "y":
        mv(old, TRASH / old_base, dryrun=dryrun)
        mv(raw, old.parent / new_base, dryrun=dryrun)
        return True
    elif accept == "?":
        print(f"\nPrinting URLs:\n\tOld: {old_data}\n\tRaw: {raw_data}\n")
    elif accept.lower() != "n":
        print("Unknown input.")
    return False


######################################################################
#                                                                    #
#                            Main Program                            #
#                                                                    #
######################################################################


def guess(directory: Path, files: list[Path], yes: bool, force: bool, dryrun: bool) -> bool:
    """
    Try to update each file in directory corresponding to a file to guess
    If yes, auto accepts proposed update; if force, ignores safety requirements
    If dryrun, nothing is actually done
    returns False on failure
    """
    directory = directory.resolve()
    assert directory.exists(), f"{directory} does not exist"
    assert directory.is_dir(), f"{directory} is not a directory"
    for i in files:
        assert not i.is_symlink(), f"{directory} may not contain links"
    files = [i.resolve() for i in files]
    for i in files:
        assert i.is_file(), f"Will not guess non-file: {i}"
    # Make trash directory
    if not dryrun:
        TRASH.mkdir(exist_ok=True)
    # For each file, try to guess
    data: dict[str, Path] = read_dir(directory)
    fails: list[Path] = []
    for f in files:
        try:
            assert guess_single(f, data, yes, force, dryrun), f"Failed to guess {f} for directory {directory}"
            print(f"\n{'-'*70}\n")
        except AssertionError as e:
            print(f"Failed for: {f}\n\t- {e}\n")
            fails.append(f)
    # If anything failed, print out info
    if fails:
        print("Failed for the following:\n\t" + "\n\t".join(str(i) for i in fails))
        return False
    print("All files properly guessed!")
    if dryrun:
        print("This was a dry run. No files were modified!")
    return True


def cli() -> None:
    assert "Darwin" == platform.system(), "Not on Mac! Remember to change name and ext!"
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true", help="Override safety checks")
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Automatically accept changes; will never prompt the user"
    )
    parser.add_argument("-n", "--dryrun", action="store_true", help="Do not actually change anything")
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        required=True,
        help="The files in this directory will be what the input files are compared against",
    )
    parser.add_argument("files", type=Path, nargs="+", help="The files to guess")
    argcomplete.autocomplete(parser)  # Tab completion
    ns = parser.parse_args()
    if ns.force and not ns.yes:
        raise RuntimeError("-f, --force requires -y, --yes")
    sys.exit(0 if guess(**vars(ns)) else -1)
