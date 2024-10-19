from dataclasses import dataclass
from functools import cache
from pathlib import Path
import logging

from zstdlib import Singleton


@dataclass
class Defaults(Singleton):
    root: logging.Logger = logging.getLogger("manga")
    path: Path = Path("/tmp/manga_scrape.log")
    level: int = logging.INFO
    file_level: int = logging.INFO
    stream_level: int = logging.WARNING
    fmt: str = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"


@cache
def get_logger(name: str) -> logging.Logger:
    d = Defaults()
    ret = d.root.getChild(name)
    ret.setLevel(d.level)
    for h, lvl in ((logging.FileHandler(d.path), d.file_level), (logging.StreamHandler(), d.stream_level)):
        h.setLevel(lvl)
        h.setFormatter(logging.Formatter(d.fmt))
        ret.addHandler(h)
    return ret
