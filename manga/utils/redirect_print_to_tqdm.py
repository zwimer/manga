import contextlib
import inspect
import tqdm


@contextlib.contextmanager
def redirect_print_to_tqdm():
    old = print
    try:
        inspect.builtins.print = tqdm.tqdm.write
        yield
    finally:
        inspect.builtins.print = old
