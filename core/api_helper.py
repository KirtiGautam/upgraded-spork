import requests
import os

API_URL = os.environ["API_URL"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
}


def get_call(path: str):
    return requests.get(f"{API_URL}{path}", headers=headers).json()
