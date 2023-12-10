from __future__ import annotations
import regex


def split_on_num(x: str, only_positive: bool = True) -> tuple[str, float, str]:
    """
    Split x at the number greater than one
    This assumes numbers end in a digit, not a decimal point
    If only_positive, negative signs will not count as part of a number
    Returns a tuple containing the string before the last number,
    the last number as a float, and the remaining string
    """
    pattern: str = r"(?r)\d*\.?\d+" if only_positive else r"(?r)-?\d*\.?\d+"
    search: regex.Match | None = regex.search(pattern, x)
    if search is None:
        raise ValueError(f"There is no number in {x}")
    num: str = search.group()
    split = x.split(num)
    return num.join(split[:-1]), float(num), split[-1]
