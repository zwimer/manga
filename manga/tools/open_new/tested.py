from dataclasses import dataclass, asdict, field
from itertools import chain


@dataclass
class Tested:
    """
    The results of testing every URL
    """

    has_new: set[str] = field(default_factory=set)
    ignore: set[str] = field(default_factory=set)
    skip: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)
    unknown: set[str] = field(default_factory=set)

    @property
    def tested(self) -> set[str]:
        return set(chain.from_iterable(asdict(self).values()))
