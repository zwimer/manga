"""
The functions in this file return true if a chapter is found for the specific site
They take in as input the html of the webpage
"""
from typing import Callable, Dict


__all__ = ("domains",)


#
# Return true if chapter is found
#


def mangakakalot_tv(data: str) -> bool:
    return "next-chap:hover" in data and "logo_chapter" in data

def mangakakalot_com(data: str) -> bool:
    return "/content/nextchap.png" not in data and \
        "Sorry, the page you have requested cannot be found. Click" not in data and \
        "already has 0 views." not in data

def mangakakalots_com(data: str) -> bool:
    return "500 Internal Server Error" not in data and \
        "Sorry, the page you have requested cannot be found. Click" not in data

def mangakakalot_cc(data: str) -> bool:
    return "nextchap.png" not in data and "is not available yet" not in data

def mangakakalot_xyz(data: str) -> bool:
    return "View: all images" in data

def mangakakalot_city(data: str) -> bool:
    return "Next Chapter:" in data and \
        "is not available yet. We will update" not in data

def mangakakalot_online(data: str) -> bool:
    return "http://mangakakalot.online/frontend/images/nextchap.png" not in data

def manganelo_com(data: str) -> bool:
    return "404 - PAGE NOT FOUND" not in data and \
        "This page does not exist or has been deleted." not in data

def manganelos_com(data: str) -> bool:
    return "is not available yet" not in data and "next_img" in data

def mangatx_com(data: str) -> bool:
    return "https://mangatx.com/wp-content/uploads/WP-manga/data/manga" in data and \
        "image-0" in data

def mangakakalot_today(data: str) -> bool:
    return "http://mangakakalot.today/frontend/imgs/nextchap.png" not in data and \
        "is not available yet. We will update " not in data

def chapmanganato_com(data: str) -> bool:
    return "404 NOT FOUND" not in data and "LOAD ALL" in data

def mangabuddy_com(data: str) -> bool:
    return '"Next chapter"' in data and '"Previous chapter"' in data


#
# Known domains
#


domains: Dict[str, Callable[[str], bool]] = {
    "mangatx.com" : mangatx_com,
    "mangabuddy.com" : mangabuddy_com,

    "manganelo.com" : manganelo_com,
    "manganelos.com" : manganelos_com,

    "mangakakalot.tv" : mangakakalot_tv,
    "mangakakalot.cc" : mangakakalot_cc,
    "mangakakalot.xyz" : mangakakalot_xyz,
    "mangakakalot.com" : mangakakalot_com,
    "mangakakalot.city" : mangakakalot_city,
    "mangakakalot.today" : mangakakalot_today,
    "mangakakalot.online" : mangakakalot_online,

    "mangakakalots.com" : mangakakalots_com,
    "mangakakalots.net" : mangakakalots_com,

    "readmanganato.com" : chapmanganato_com,
    "chapmanganato.com" : chapmanganato_com,
}
