import contextlib
import inspect
import tqdm


def _print(obj, **kwargs):
    tqdm.tqdm.write(obj if isinstance(obj, str) else str(obj))


@contextlib.contextmanager
def redirect_print_to_tqdm():
    old = print
    try:
        inspect.builtins.print = _print
        yield
    finally:
        inspect.builtins.print = old
