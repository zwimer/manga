from typing import Tuple, List
from pathlib import Path
import argparse
import sys
import os

from manga.utils import extract_url_from_contents, split_on_num, mv


def inc_str(x: str) -> str:
    """
    Increment the last number in x
    """
    assert any(c.isdigit() for c in x), f"No number detected in {x}"
    left, num, right = split_on_num(x)
    new: str = str((int(num) if num == int(num) else num) + 1)
    return left + new + right


def find_url(data: str, ext: str) -> Tuple[str, str, str]:
    """
    Split data into by the found URL
    Return the data on the left, the URL, and the data on the right
    """
    url: str = extract_url_from_contents(data, ext)
    sides: List[str] = data.split(url) + [""]
    assert len(sides) <= 3, "URL repeated in data"
    return sides[0], url, sides[1]


def inc_chapter(file: Path, url_only: bool, yes: bool, dryrun: bool) -> bool:
    """
    Increment the number in both the URL and name of file
    """
    absolute: Path = file.absolute()
    file = file.resolve()
    assert file == absolute, f"{file} should not contain symlinks"
    assert file.exists(), f"{file} does not exist"
    assert file.is_file(), f"{file} is not a file"
    # Pre-check + extract url
    base: str = file.name
    with file.open("r") as f:
        data: str = f.read()
    left, url, right = find_url(data, file.suffix)
    # Increment required items
    new_url: str = inc_str(url)
    new_base: str = base if url_only else inc_str(base)
    # Prompt
    print(f"\nOld: {base}\n\tURL: {url}\nNew: {new_base}\n\tURL: {new_url}\n")
    if yes:
        print("Auto accepting.")
        accept = "y"
    else:
        print("Accept? [N/?/y]")
        accept = input()
    # Act on prompt input
    if accept == "y":
        print("")
        output: str = left + new_url + right
        if dryrun:
            print("This is a dry run!")
        else:
            with file.open("w") as f:
                f.write(output)
        if not url_only:
            mv(file, file.parent / new_base, dryrun=dryrun)
        return True
    elif accept.lower() != "n":
        print("Unknown input.")
    return False


def main(prog: str, *args: str) -> bool:
    parser = argparse.ArgumentParser(prog=os.path.basename(prog))
    parser.add_argument("-y", "--yes", action="store_true",
        help="Automatically accept changes; will never prompt the user")
    parser.add_argument("-n", "--dryrun", action="store_true",
        help="Do not actually change anything")
    parser.add_argument('-u', '--url_only', action='store_true',
        help="Only increment the URL, not the file name")
    parser.add_argument("file", type=Path, help="The file to increment the numbers of")
    return inc_chapter(**vars(parser.parse_args(args)))


def cli() -> None:
    sys.exit(0 if main(*sys.argv) else -1)
