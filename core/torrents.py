from typing import List
from core import api_helper
from core.constants import CATEGORIES, TRACKERS


def get_categories():
    """Returns formatted string of all available categories and subcategories."""
    data = ""
    for category in CATEGORIES.keys():
        data += f"- {category.title()}\n"
        for subcategory in CATEGORIES[category].keys():
            data += f"  - {subcategory}\n"

    return data


def order_results(result) -> List:
    """Sorts torrent results by seeders in descending order."""
    return sorted(result, key=lambda d: int(d["seeders"]), reverse=True)


def list_torrents(q: str, category: str = None, subcategory: str = None) -> List:
    """
    Fetches torrents from API based on search query and optional category/subcategory.
    
    Args:
        q: Search query string
        category: Optional category name
        subcategory: Optional subcategory name
    
    Returns:
        List of top 10 torrents sorted by seeders
    """
    code = CATEGORIES[category][subcategory] if category and subcategory else ""
    result = api_helper.get_call(f"q.php?q={q}&cat={code}")
    return order_results(result)[0:10]


def generate_magnet_link(info_hash: str, with_trackers: bool = True) -> str:
    """
    Generates a magnet link from a torrent info_hash.
    
    Args:
        info_hash: The torrent's info hash
    
    Returns:
        Magnet link string
    """
    link = f"magnet:?xt=urn:btih:{info_hash}"
    if with_trackers:
        link += TRACKERS
    return link


def invalid_category(category, subcategory):
    """
    Validates if a category and subcategory combination exists.
    
    Args:
        category: Category name to validate
        subcategory: Subcategory name to validate
    
    Returns:
        True if invalid, False if valid
    """
    if (category not in CATEGORIES) or (subcategory not in CATEGORIES[category]):
        return True
    return False


def handle_search(message: str):
    """
    Parses search message and returns torrent results.
    
    Message format: "search_term - category - subcategory"
    Category and subcategory are optional.
    
    Args:
        message: Search message string
    
    Returns:
        List of torrents or False if invalid category/subcategory
    """
    command = message.lower().split("-")
    q = command[0].strip()
    category = command[1].strip() if len(command) > 1 else ""
    subcategory = command[2].strip() if len(command) > 2 else ""
    if (category and subcategory) and invalid_category(category, subcategory):
        return False
    return list_torrents(q, category, subcategory)
