from typing import List
from torrent import api_helper
from torrent.constants import CATEGORIES, PARAMS


def get_categories():
    data = ""
    for category in CATEGORIES.keys():
        data += f"- {category.title()}\n"
        for subcategory in CATEGORIES[category].keys():
            data += f"  - {subcategory}\n"

    return data


def order_results(result) -> List:
    return sorted(result, key=lambda d: int(d["seeders"]), reverse=True)


def list_torrents(q: str, category: str = None, subcategory: str = None) -> List:
    code = CATEGORIES[category][subcategory] if category and subcategory else ""
    result = api_helper.get_call(f"q.php?q={q}&cat={code}")
    return order_results(result)[0:10]


def generate_magnet_link(info_hash: str) -> str:
    link = f"magnet:?xt=urn:btih:{info_hash}{PARAMS}"
    return link

def invalid_category(category, subcategory):
    if (category not in CATEGORIES) or (subcategory not in CATEGORIES[category]):
        return True
    return False

def handle_search(message: str):
    command = message.lower().split("-")
    q = command[0].strip()
    category = command[1].strip() if len(command) > 1 else ""
    subcategory = command[2].strip() if len(command) > 2 else ""
    if (category and subcategory) and invalid_category(category, subcategory):
        return False
    return list_torrents(q, category, subcategory)
