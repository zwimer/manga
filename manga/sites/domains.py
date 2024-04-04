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
    return "404 NOT FOUND" not in data and "LOAD ALL" in data


def chapmanganato_com(data: str) -> bool:
    return "404 NOT FOUND" not in data and "LOAD ALL" in data


def mangabuddy_com(data: str) -> bool:
    return '"Next chapter"' in data and '"Previous chapter"' in data


def mangaclash_com(data: str) -> bool:
    return "cursorNext" in data and "Alternative" not in data


def manhuascan_com(data: str) -> bool:
    return "loadchapter" in data and "chapterNumber = null" not in data


def manhuafast_com(data: str) -> bool:
    return "backInfoPage" in data and "Read Last" not in data


def manhuafast_net(data: str) -> bool:
    return "prev_page" in data and "Read Last" not in data


def manhuaus_org(data: str) -> bool:
    return "prev_page" in data and "main-menu" not in data


def manhwatop_com(data: str) -> bool:
    return "loader.svg" in data and "Show more" not in data


def zinmanga_com(data: str) -> bool:
    return "single-chapter-select" in data and "TRENDING" not in data


#
# Known domains
#


domains: dict[str, Callable[[str], bool]] = {
    "mangatx.com": mangatx_com,
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
    "manhuascan.com": manhuascan_com,
    "manhuafast.com": manhuafast_com,
    "manhuafast.net": manhuafast_net,
    "manhuaus.org": manhuaus_org,
    "manhwatop.com": manhwatop_com,
    "zinmanga.com": zinmanga_com,
}
