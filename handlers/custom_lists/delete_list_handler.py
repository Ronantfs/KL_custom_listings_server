"""
Route 5: Delete a custom list.

Payload specifies curator and list_name. Removes the list entirely
from the curator's filmLists.json.
"""

import logging
from typing import Dict, Any

from core.s3 import get_s3_client, download_json_from_s3, upload_dict_to_s3
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX, FILM_LISTS_FILENAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def delete_list_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    curator: str = event["curator"]
    list_name: str = event["list_name"]

    logger.info("delete_list_handler curator=%s list_name=%s", curator, list_name)

    s3 = get_s3_client()
    lists_key = f"{FILM_LISTS_BASE_PREFIX}/{curator}/{FILM_LISTS_FILENAME}"
    film_lists = download_json_from_s3(s3, S3_BUCKET, lists_key)

    original_count = len(film_lists)
    film_lists = [fl for fl in film_lists if fl["list_name"] != list_name]

    if len(film_lists) == original_count:
        raise ValueError(f"List '{list_name}' not found for curator '{curator}'")

    upload_dict_to_s3(s3, S3_BUCKET, lists_key, film_lists)

    return {
        "status": "ok",
        "curator": curator,
        "deleted_list": list_name,
        "remaining_lists": len(film_lists),
        "output_uri": f"s3://{S3_BUCKET}/{lists_key}",
    }
