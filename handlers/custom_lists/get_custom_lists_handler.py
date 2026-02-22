"""
Route 1: Get custom lists for a given curator.

Downloads s3://filmfynder/london/filmLists/{curator}/filmLists.json
and returns the list of CustomList objects.
"""

import logging
from typing import Dict, Any

from core.s3 import get_s3_client, download_json_from_s3
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX, FILM_LISTS_FILENAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_custom_lists_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    curator: str = event["curator"]
    logger.info("get_custom_lists_handler curator=%s", curator)

    s3 = get_s3_client()
    key = f"{FILM_LISTS_BASE_PREFIX}/{curator}/{FILM_LISTS_FILENAME}"

    try:
        film_lists = download_json_from_s3(s3, S3_BUCKET, key)
    except FileNotFoundError:
        film_lists = []

    return {
        "status": "ok",
        "curator": curator,
        "lists_count": len(film_lists),
        "film_lists": film_lists,
    }
