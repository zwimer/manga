from collections import defaultdict

from manga.sites import get_domain

from .status import Status, Untested


_untested = Untested()


class URL:
    def __init__(self, url: str) -> None:
        self.url = url
        self.domain = get_domain(url)
        self.status: Status = _untested

    def __str__(self):
        return self.url

    def __repr__(self):
        return f'<URL: "{self.url}" - {self.status.__class__.__name__}>'


class State:
    def __init__(self, urls: set[str]) -> None:
        self._urls: tuple[URL, ...] = tuple(URL(i) for i in urls)

    def __len__(self) -> int:
        return len(self._urls)

    def domains(self) -> dict[str, list[URL]]:
        bucketed = defaultdict(list)
        for i in self._urls:
            bucketed[i.domain].append(i)
        return bucketed

    def get(self, status_type: type[Status]) -> tuple[URL, ...]:
        return tuple(i for i in self._urls if isinstance(i.status, status_type))
