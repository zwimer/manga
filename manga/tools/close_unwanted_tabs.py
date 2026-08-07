from dataclasses import dataclass, field
import threading
import argparse
import re

from tqdm import tqdm
import tldextract
import osascript


@dataclass(kw_only=True, frozen=True, eq=True, slots=True)
class Tab:
    window_id: int = field(repr=False)
    id_: int = field(repr=False)
    index: int
    url: str
    title: str
    html: str = field(repr=False)


class Cycler:
    """Cycle through tabs in the browser window to force each javascript engine to start"""

    def __init__(self, window_id: int, n_tabs: int) -> None:
        self._thread: threading.Thread | None = None
        self.window_id: int = window_id
        self.n_tabs: int = n_tabs
        self._quit: bool = False

    def start(self) -> None:
        assert threading.current_thread() is threading.main_thread()
        self._thread = threading.Thread(target=self._start)
        self._thread.start()

    def _start(self) -> None:
        assert threading.current_thread() is not threading.main_thread()
        for i in range(self.n_tabs):
            tell_brave(*get_window_cmds(self.window_id, "w"), f"set active tab index of w to {i+1}")
            if self._quit:
                break

    def stop(self) -> None:
        assert threading.current_thread() is threading.main_thread()
        if self._thread is not None:
            self._quit = True
            self._thread.join()


def pbar(x, desc: str, *, leave: bool = False) -> tqdm:
    return tqdm(list(x), desc=desc, leave=leave, dynamic_ncols=True)


def tell_brave(*lines: str) -> str:
    """Applescript, tell brave to execute lines"""
    code, out, err = osascript.run(f'tell application "Brave Browser"\n{"\n".join(lines)}\nend')
    assert code == 0 and err == "", err
    return out


def get_window_cmds(window_id: int, name: str) -> tuple[str, ...]:
    """Applescript lines that set the desired window to the variable: name"""
    return (
        f'set wins to every window whose id is "{window_id}"',
        'if length of wins is not 1 then error "Wrong number of windows"',  # Sanity check
        f"set {name} to (item 1 of wins)",
    )


def get_tab(window_id: int, index: int) -> Tab:
    """Get the index'th tab of the given window"""
    w_id, id_, full_url, title, html = tell_brave(
        *get_window_cmds(window_id, "w"),
        f"set x to tab {index} of w",
        'set html to execute x javascript "document.documentElement.outerHTML"',
        'return (id of w) & "\n" & (id of x) & "\n" & (URL of x) & "\n" & (title of x) & "\n" & html',
    ).split("\n", 4)
    url = full_url.split("#", 1)[0].split("?", 1)[0]
    return Tab(window_id=int(w_id), id_=int(id_), index=index, url=url, title=title, html=html)


def close_tab(tab: Tab) -> None:
    """Close the given tab"""
    _ = tell_brave(
        *get_window_cmds(tab.window_id, "w"),
        f'tell w to set bad_tabs to every tab whose id is "{tab.id_}"',
        'if length of bad_tabs is not 1 then error "Wrong number of tabs"',  # Sanity check
        "tell (item 1 of bad_tabs) to close",
    )


def check_unwanted_tab(tab: Tab) -> bool:
    """Check if the given tab is wanted based only on its contents"""
    if tab.title in {
        "",
        "Error 404",
        "Page Not Found - Raven Scans",
        "Page not found – Raven Scans",
    }:
        return True
    match (tld := tldextract.extract(tab.url).top_domain_under_public_suffix):
        case "mangak.io":
            return '>Page Not Found</h2><p class="text-fg-muted text-sm mb-6">Not Found<' in tab.html
        case "mangahub.io":
            return tab.url.split(tld, 1)[1].startswith("/manga/")
        case "mangafreak.me":
            return not tab.url.split(tld, 1)[1].lstrip("/")
        case "manhuaus.com":
            return "</i>LATESTMANGARELEASES</h2>" in re.sub(r"\s+", "", tab.html, flags=re.MULTILINE)
        case "philiascans.org":
            bad = (
                """>You're missing<br>the <span class="reg-accent">free unlock<""",
                ">Set, lettered and waiting. Open it once and it’s yours for good — tonight, or years from now.<",
                'aria-label="404 — page not found"',
            )
            return any(i in tab.html for i in bad)
    return False


def close_unwanted_tabs(no_close_dupes: bool, no_cycle_tabs: bool) -> None:
    """Determine which tabs are unwanted and close them"""

    # Gather window data
    n_tabs, w_id = (int(i) for i in re.sub('["{},]', "", tell_brave("{count tabs, id} of front window")).split(" "))

    # Prelaod tabs if desired
    cycler = Cycler(w_id, n_tabs)
    if not no_cycle_tabs:
        cycler.start()

    # Gather tab data
    tabs = [get_tab(w_id, i) for i in pbar(range(1, n_tabs + 1), "Scanning tabs")]
    assert len(win_ids := {i.window_id for i in tabs}) == 1, f"Wrong number of window ids: {win_ids}"

    # Determine bad tabs (prefer left tabs to right tabs if dupes)
    bad = []
    if not no_close_dupes:
        for url in {i.url for i in tabs}:
            bad += sorted((k for k in tabs if k.url == url), key=lambda x: x.index)[1:]
    bad += [i for i in set(tabs) - set(bad) if check_unwanted_tab(i)]
    cycler.stop()

    # Close bad tabs
    if bad:
        if len(bad) == n_tabs:
            print("All tabs unwanted, closing window...", flush=True)
            tell_brave(*get_window_cmds(w_id, "w"), "tell w to close")
        else:
            print("Found bad tabs:\n  " + "\n  ".join(sorted(i.url for i in bad)), flush=True)
            for tab in pbar(sorted(bad, key=lambda x: x.index), "Closing tabs", leave=True):
                close_tab(tab)
    else:
        print("No bad tabs found")
    print("Success")


def cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-cycle-tabs",
        action="store_true",
        help="Do not cycle the window tabs to ensure each can run javascript before checking",
    )
    parser.add_argument("--no-close-dupes", action="store_true", help="Do not close duplicate tabs")
    close_unwanted_tabs(**vars(parser.parse_args()))


if __name__ == "__main__":
    cli()
