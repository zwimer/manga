from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
from concurrent.futures import thread

from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn, TaskProgressColumn

if TYPE_CHECKING:
    from concurrent.futures import Future
    from collections.abc import Callable
    from typing import Any

if TYPE_CHECKING:
    from .state import URL, State


class _ThreadHandler(thread.ThreadPoolExecutor):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.futures: list[Future] = []

    def add(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.futures.append(super().submit(fn, *args, **kwargs))

    def kill(self):
        self.shutdown(wait=False)
        for i in self.futures:
            i.cancel()


class FuncType(Protocol):
    def __call__(self, urls: list[URL], update_pbar: Callable[[], None], *args: Any, **kwargs: Any) -> None: ...


def dispatch(state: State, func: FuncType, *args: Any, **kwargs: Any) -> None:
    buckets = state.domains()
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        TaskProgressColumn(),
        BarColumn(None),
        MofNCompleteColumn(),
        TimeRemainingColumn(compact=True, elapsed_when_finished=True),
        transient=True,
        expand=True,
    ) as pbar:
        with _ThreadHandler(max_workers=len(buckets)) as executor:  # No DOS-ing
            for domain, urls in buckets.items():
                task = pbar.add_task(f"{domain}:", total=len(urls))
                executor.add(func, urls, lambda bound=task: pbar.update(bound, advance=1), *args, **kwargs)
