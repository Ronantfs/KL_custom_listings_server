"""
Route 4: Update list metadata (not the films).

Payload specifies curator, list_name, and any fields to update:
  list_caption, start_date, end_date, new_list_name.
"""

import logging
import re
from typing import Dict, Any

from core.s3 import get_s3_client, download_json_from_s3, upload_dict_to_s3
from core.types.custom_lists import CuratorFilmLists, validate_curator_film_lists
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX, FILM_LISTS_FILENAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

UPDATABLE_FIELDS = {"list_name", "list_caption", "start_date", "end_date"}


def update_list_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    curator: str = event["curator"]
    list_name: str = event["list_name"]
    updates: Dict[str, str] = event.get("updates", {})

    logger.info(
        "update_list_handler curator=%s list_name=%s updates=%s",
        curator, list_name, list(updates.keys()),
    )

    if not updates:
        raise ValueError("No updates provided")

    invalid_keys = set(updates.keys()) - UPDATABLE_FIELDS
    if invalid_keys:
        raise ValueError(f"Cannot update fields: {', '.join(invalid_keys)}")

    # Validate date formats if provided
    for date_field in ("start_date", "end_date"):
        if date_field in updates and not DATE_PATTERN.match(updates[date_field]):
            raise ValueError(f"Invalid {date_field} format '{updates[date_field]}', expected YYYY-MM-DD")

    s3 = get_s3_client()
    lists_key = f"{FILM_LISTS_BASE_PREFIX}/{curator}/{FILM_LISTS_FILENAME}"
    raw = download_json_from_s3(s3, S3_BUCKET, lists_key)
    film_lists: CuratorFilmLists = validate_curator_film_lists(raw, curator)

    # Find target list
    target_list = None
    for fl in film_lists:
        if fl["list_name"] == list_name:
            target_list = fl
            break

    if target_list is None:
        raise ValueError(f"List '{list_name}' not found for curator '{curator}'")

    updated_fields = []
    for field, value in updates.items():
        target_list[field] = value
        updated_fields.append(field)

    upload_dict_to_s3(s3, S3_BUCKET, lists_key, film_lists)

    return {
        "status": "ok",
        "curator": curator,
        "list_name": target_list["list_name"],
        "updated_fields": updated_fields,
        "output_uri": f"s3://{S3_BUCKET}/{lists_key}",
    }
