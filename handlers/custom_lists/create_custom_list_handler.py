"""
Route 2: Create a new custom list.

Takes a payload with all required fields and creates a new list
(starting with no films assigned). Saves to the curator's filmLists.json.
"""

import logging
import re
from typing import Dict, Any

from core.s3 import get_s3_client, download_json_from_s3, upload_dict_to_s3
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX, FILM_LISTS_FILENAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_FIELDS = ["curator", "list_name", "list_caption", "start_date", "end_date"]


def create_custom_list_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    # Validate required fields
    missing = [f for f in REQUIRED_FIELDS if not event.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    curator: str = event["curator"]
    list_name: str = event["list_name"]
    list_caption: str = event["list_caption"]
    start_date: str = event["start_date"]
    end_date: str = event["end_date"]

    logger.info("create_custom_list_handler curator=%s list_name=%s", curator, list_name)

    # Validate date formats
    if not DATE_PATTERN.match(start_date):
        raise ValueError(f"Invalid start_date format '{start_date}', expected YYYY-MM-DD")
    if not DATE_PATTERN.match(end_date):
        raise ValueError(f"Invalid end_date format '{end_date}', expected YYYY-MM-DD")

    s3 = get_s3_client()
    key = f"{FILM_LISTS_BASE_PREFIX}/{curator}/{FILM_LISTS_FILENAME}"

    # Load existing lists or start fresh
    try:
        film_lists = download_json_from_s3(s3, S3_BUCKET, key)
    except FileNotFoundError:
        film_lists = []

    # Check for duplicate list name
    for existing in film_lists:
        if existing["list_name"] == list_name:
            raise ValueError(f"List '{list_name}' already exists for curator '{curator}'")

    new_list = {
        "list_curator": curator,
        "list_name": list_name,
        "list_caption": list_caption,
        "start_date": start_date,
        "end_date": end_date,
        "list_films": [],
    }

    film_lists.append(new_list)
    upload_dict_to_s3(s3, S3_BUCKET, key, film_lists)

    return {
        "status": "ok",
        "curator": curator,
        "list_name": list_name,
        "lists_total": len(film_lists),
        "output_uri": f"s3://{S3_BUCKET}/{key}",
    }
