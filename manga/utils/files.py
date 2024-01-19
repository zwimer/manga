from __future__ import annotations
from collections.abc import Iterable
from pathlib import Path


__all__ = ("lsf", "mv")


def lsf(d: Path) -> tuple[Path, ...]:
    """
    ls all files in d recursively, but ignore likely undesired files
    """
    each: Iterable[Path] = (i.resolve() for i in d.resolve().rglob("*"))
    ignore: set[str] = {".DS_Store"}
    return tuple(i for i in each if i.is_file() and i.name not in ignore)


def mv(a: Path, b: Path, *, dryrun: bool = False) -> None:
    """
    Rename a to b
    """
    a = a.resolve()
    b = b.resolve()
    print(f"{a} --> {b}")
    if not dryrun:
        a.rename(b)
