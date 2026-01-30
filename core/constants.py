import os

# Torrent trackers for magnet links
TRACKERS = os.environ.get('PARAMS', '')

CATEGORIES = {
    "audio": {
        "music": "101",
        "flac": "104",
        "other": "199",
    },
    "video": {
        "movies": "201",
        "handheld": "206",
        "3d": "209",
        "other": "299",
    },
    "applications": {
        "windows": "301",
        "mac": "302",
        "unix": "303",
        "handheld": "304",
        "ios": "305",
        "android": "306",
        "other": "399",
    },
    "games": {
        "pc": "401",
        "mac": "402",
        "psx": "403",
        "xbox360": "404",
        "wii": "405",
        "handheld": "406",
        "ios": "407",
        "android": "408",
        "other": "499",
    },
    "porn": {
        "movies": "501",
        "pictures": "503",
        "games": "504",
        "other": "599",
    },
    "other": {
        "e-books": "601",
        "comics": "602",
        "pictures": "603",
        "covers": "604",
        "physibles": "605",
        "other": "699",
    },
}
