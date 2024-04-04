from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
from concurrent.futures import thread
import signal

if TYPE_CHECKING:
    from concurrent.futures import Future
    from typing import Any


class _SigintHandler(Protocol):
    def __call__(self, executor: ThreadHandler, *args: Any):
        pass


class ThreadHandler(thread.ThreadPoolExecutor):
    def __init__(self, sigint_handler: _SigintHandler, *args: Any, **kwargs: Any):
        self._handler = lambda *x: sigint_handler(self, *x)
        super().__init__(*args, **kwargs)
        self.futures: list[Future] = []

    def add(self, fn, *args: Any, **kwargs: Any) -> None:
        self.futures.append(super().submit(fn, *args, **kwargs))

    def kill(self):
        self.shutdown(wait=False)
        for i in self.futures:
            i.cancel()

    def __enter__(self) -> ThreadHandler:
        self._orig: Any = signal.signal(signal.SIGINT, self._handler)
        rv = super().__enter__()
        assert rv is self
        return self

    def __exit__(self, *args):
        super().__exit__(*args)
        signal.signal(signal.SIGINT, self._orig)
