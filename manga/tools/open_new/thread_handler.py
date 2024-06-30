from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
from concurrent.futures import thread
import signal

if TYPE_CHECKING:
    from concurrent.futures import Future
    from typing import Any


class _SignalHandler(Protocol):
    def __call__(self, executor: ThreadHandler, *args: Any):
        pass


class ThreadHandler(thread.ThreadPoolExecutor):
    def __init__(self, handlers: dict[signal.Signals, _SignalHandler], *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._handlers = dict(handlers)
        self.futures: list[Future] = []

    def _install_handler(self, s: signal.Signals, f: _SignalHandler) -> Any:
        def ret(*x):
            return f(self, *x)

        return signal.signal(s, ret)

    def add(self, fn, *args: Any, **kwargs: Any) -> None:
        self.futures.append(super().submit(fn, *args, **kwargs))

    def kill(self):
        self.shutdown(wait=False)
        for i in self.futures:
            i.cancel()

    def __enter__(self) -> ThreadHandler:
        self._orig: dict[signal.Signals, Any] = {s: self._install_handler(s, f) for s, f in self._handlers.items()}
        rv = super().__enter__()
        assert rv is self
        return self

    def __exit__(self, *args):
        super().__exit__(*args)
        for s, f in self._orig.items():
            signal.signal(s, f)
