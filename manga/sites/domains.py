"""
The functions in this file return true if a chapter is found for the specific site
They take in as input the html of the webpage
"""

from __future__ import annotations
from collections.abc import Callable


#
# Return true if chapter is found
#


def mangakakalot_gg(data: str) -> bool:
    return "next" in data and "PREV CHAPTER" in data and "moveToListChapter" not in data


def natomanga_com(data: str) -> bool:
    return "next" in data and "PREV CHAPTER" in data and "moveToListChapter" not in data


def mangabuddy_com(data: str) -> bool:
    return '"Next chapter"' in data and '"Previous chapter"' in data


def toonclash_com(data: str) -> bool:
    return "cursorNext" in data and "Alternative" not in data


def mangaclash_com(data: str) -> bool:
    return "cursorNext" in data and "Alternative" not in data


def manhwatop_com(data: str) -> bool:
    return "Next" in data and "Show more" not in data


def kunmanga_com(data: str) -> bool:
    return "chapters_selectbox_holder" in data and "LATEST MANGA RELEASES" not in data


def harimanga_me(data: str) -> bool:
    return '"prev":"Prev","next":"Next' in data and "#manga-discussion" not in data


def harimanga_com(data: str) -> bool:
    return '"prev":"Prev","next":"Next' in data and "#manga-discussion" not in data


def oniscan_com(data: str) -> bool:
    return "next-nav" in data and "Last Releases" not in data


def mangakatana_com(data: str) -> bool:
    return "send_img_err = false" in data and 'prev" disabled="disabled' not in data


# Special functions


def true_(_: str) -> bool:
    return True


#
# Known domains
#


domains: dict[str, Callable[[str], bool]] = {
    "mangakakalot.gg": mangakakalot_gg,
    "natomanga.com": natomanga_com,
    #
    "toonclash.com": toonclash_com,
    "mangaclash.com": mangaclash_com,
    "mangabuddy.com": mangabuddy_com,
    #
    "harimanga.com": harimanga_com,
    "harimanga.me": harimanga_me,
    #
    "mangakatana.com": mangakatana_com,
    "manhwatop.com": manhwatop_com,
    "kunmanga.com": kunmanga_com,
    "oniscan.com": oniscan_com,
    #
    # Returns 404 if no new chapter
    #
    "manhwabuddy.com": true_,
    "kingofshojo.com": true_,
    "rackusreads.com": true_,
    "mangareader.to": true_,
    "mgeko.cc": true_,
}
