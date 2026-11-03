from dataclasses import dataclass, asdict, field


@dataclass
class Tested:
    """The results of testing every URL"""

    has_new: set[str] = field(default_factory=set)
    ignore: set[str] = field(default_factory=set)
    skip: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)
    unknown: set[str] = field(default_factory=set)

    @property
    def tested(self) -> set[str]:
        return {*it for it in asdict(self).values()}
