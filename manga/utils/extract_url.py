from __future__ import annotations
from pathlib import Path


__all__ = ("extract_url_from_contents", "extract_url")


def _half(what: str, where: str) -> tuple[str, str]:
    ret: list[str] = what.split(where)
    assert len(ret) == 2, f"{what} does not contain {where} exactly once"
    return ret[0], ret[1]


def extract_url_from_contents(data: str, extension: str) -> str:
    """
    Extract the URL from the file data
    """
    upper: str
    lower: str
    if ".url" == extension:
        upper = _half(data, "URL=")[1]
    elif ".desktop" == extension:
        lower = _half(data, "URL=")[1]
        upper = _half(lower, "Icon=")[0]
    elif ".webloc" == extension:
        lower = _half(data, "<string>")[1]
        upper = _half(lower, "</string>")[0]
    else:
        raise ValueError(f"Unsupported extension: {extension}")
    url: str = upper.strip()
    assert len(url), "Failed to extract url"
    return url


def extract_url(file: Path):
    """
    Extract the URL from the file
    """
    file = file.resolve()
    assert file.exists(), f"{file} does not exist"
    assert file.suffix, f"{file} has no extension"
    try:
        data = file.read_text()
    except UnicodeDecodeError as e:
        raise RuntimeError(f"Failed to read: {file}") from e
    return extract_url_from_contents(data.strip(), file.suffix)
