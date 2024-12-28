"""
The functions in this file return true if a chapter is found for the specific site
They take in as input the html of the webpage
"""

from __future__ import annotations
from collections.abc import Callable


#
# Return true if chapter is found
#


def mangakakalot_tv(data: str) -> bool:
    return "next-chap:hover" in data and "logo_chapter" in data


def mangakakalot_com(data: str) -> bool:
    return (
        "nextchap.png" not in data
        and "Sorry, the page you have requested cannot be found." not in data
        and "PREV CHAPTER" in data
    )


def mangakakalots_com(data: str) -> bool:
    return (
        "500 Internal Server Error" not in data
        and "Sorry, the page you have requested cannot be found. Click" not in data
    )


def mangakakalot_cc(data: str) -> bool:
    return "nextchap.png" not in data and "is not available yet" not in data


def mangakakalot_xyz(data: str) -> bool:
    return "View: all images" in data


def mangakakalot_city(data: str) -> bool:
    return "Next Chapter:" in data and "is not available yet. We will update" not in data


def mangakakalot_online(data: str) -> bool:
    return "http://mangakakalot.online/frontend/images/nextchap.png" not in data


def manganelo_com(data: str) -> bool:
    # This still returns an ok status, it just says 404
    return "404 - PAGE NOT FOUND" not in data and "This page does not exist or has been deleted." not in data


def manganelos_com(data: str) -> bool:
    return "is not available yet" not in data and "next_img" in data


def mangatx_com(data: str) -> bool:
    return "https://mangatx.com/wp-content/uploads/WP-manga/data/manga" in data and "image-0" in data


def mangakakalot_today(data: str) -> bool:
    return (
        "http://mangakakalot.today/frontend/imgs/nextchap.png" not in data
        and "is not available yet. We will update " not in data
    )


def chapmanganato_to(data: str) -> bool:
    # This still returns an ok status, it just says 404
    return "404 NOT FOUND" not in data and "LOAD ALL" in data


def chapmanganato_com(data: str) -> bool:
    # This still returns an ok status, it just says 404
    return "404 NOT FOUND" not in data and "LOAD ALL" in data


def mangabuddy_com(data: str) -> bool:
    return '"Next chapter"' in data and '"Previous chapter"' in data


def toonclash_com(data: str) -> bool:
    return "cursorNext" in data and "Alternative" not in data


def mangaclash_com(data: str) -> bool:
    return "cursorNext" in data and "Alternative" not in data


def manhuascan_com(data: str) -> bool:
    return "loadchapter" in data and "chapterNumber = null" not in data


def manhuaus_com(data: str) -> bool:
    return "btn prev_page" in data and "Show more" not in data


def manhuaus_org(data: str) -> bool:
    return "prev_page" in data and "main-menu" not in data


def manhwatop_com(data: str) -> bool:
    return "loader.svg" in data and "Show more" not in data


def manhwatop_org(data: str) -> bool:
    return "Next" in data and "Show more" not in data


def zinmanga_com(data: str) -> bool:
    return "single-chapter-select" in data and "TRENDING" not in data


def kunmanga_com(data: str) -> bool:
    return "chapters_selectbox_holder" in data and "LATEST MANGA RELEASES" not in data


def manga4life_com(data: str) -> bool:
    return "CurChapter" in data and "Next" in data and "mx-auto QuickSearch" not in data


def harimanga_me(data: str) -> bool:
    return '"prev":"Prev","next":"Next' in data and "#manga-discussion" not in data


def harimanga_com(data: str) -> bool:
    return '"prev":"Prev","next":"Next' in data and "#manga-discussion" not in data


def oniscan_com(data: str) -> bool:
    return "next-nav" in data and "Next" not in data


def mangakatana_com(data: str) -> bool:
    return "send_img_err = false" in data and 'prev" disabled="disabled' not in data


# Special functions


def true_(_: str) -> bool:
    return True


#
# Known domains
#


domains: dict[str, Callable[[str], bool]] = {
    "mangatx.com": mangatx_com,
    "toonclash.com": toonclash_com,
    "mangaclash.com": mangaclash_com,
    "mangabuddy.com": mangabuddy_com,
    #
    "manganelo.com": manganelo_com,
    "manganelos.com": manganelos_com,
    #
    "mangakakalot.tv": mangakakalot_tv,
    "mangakakalot.cc": mangakakalot_cc,
    "mangakakalot.xyz": mangakakalot_xyz,
    "mangakakalot.com": mangakakalot_com,
    "mangakakalot.city": mangakakalot_city,
    "mangakakalot.today": mangakakalot_today,
    "mangakakalot.online": mangakakalot_online,
    #
    "mangakakalots.com": mangakakalots_com,
    "mangakakalots.net": mangakakalots_com,
    #
    "readmanganato.com": chapmanganato_com,
    "chapmanganato.com": chapmanganato_com,
    "chapmanganato.to": chapmanganato_to,
    #
    "harimanga.com": harimanga_com,
    "harimanga.me": harimanga_me,
    #
    "manhuaus.com": manhuaus_com,
    "manhuaus.org": manhuaus_org,
    #
    "mangakatana.com": mangakatana_com,
    "manga4life.com": manga4life_com,
    "manhuascan.com": manhuascan_com,
    "manhwatop.com": manhwatop_com,
    "manhuatop.org": manhwatop_org,
    "zinmanga.com": zinmanga_com,
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
