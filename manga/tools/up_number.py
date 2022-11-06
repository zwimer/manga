from manga.utils import split_on_num, mv

from pathlib import Path
import argparse
import sys
import os


def up_number(file: Path, number: int, yes: bool) -> bool:
    absolute: Path = file.absolute()
    file = file.resolve()
    # Santiy check
    assert file == absolute, f"{file} may not contain symlinks"
    assert file.exists(), f"{file} does not exist"
    assert file.is_file(), f"{file} is not a file"
    if file.suffix != ".webloc":
        print(f"{file} is not webloc!")
        sys.exit(1)
    # Calculate new name
    left, old_n, right = split_on_num(file.name)
    assert len(left) != 0, f"Something is wrong with the name of {file}"
    assert old_n <= number, f"New number {number} is not greater than old number {old_n}"
    n_str = str(int(number) if round(number) == number else number)
    new: Path = file.parent / (left + n_str + right)
    # Prompt user
    print(f"Old: {file.name}\nNew: {new.name}\n\nAccept? [N/y]")
    accept: str = "y" if yes else input()
    if accept == "y":
        if yes:
            print("Auto Accepting.")
        mv(file, new)
        return True
    elif accept != "n":
        print("Unknown input")
    return False


def main(prog: str, *args: str) -> bool:
    parser = argparse.ArgumentParser(prog=os.path.basename(prog))
    parser.add_argument("-y", "--yes", action="store_true",
        help="Automatically accept changes; will never prompt the user")
    parser.add_argument("file", type=Path, help="The file to increase the number of")
    parser.add_argument("number", type=float, help="The number to increment file to")
    return up_number(**vars(parser.parse_args(args)))


def cli() -> None:
    sys.exit(0 if main(*sys.argv) else -1)
