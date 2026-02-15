from app.database.db import get_cached_scan, save_scan


def check_cache(text: str):
    return get_cached_scan(text)


def store_cache(text: str, response: dict):
    save_scan(text, response)
