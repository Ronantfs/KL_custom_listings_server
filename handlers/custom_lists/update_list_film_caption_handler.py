"""
Route 3.3: Update the caption of a specific film in a custom list.

Payload specifies curator, list_name, db_id, and new_caption.
"""

import logging
from typing import Dict, Any

from core.s3 import get_s3_client, download_json_from_s3, upload_dict_to_s3
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX, FILM_LISTS_FILENAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def update_list_film_caption_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    curator: str = event["curator"]
    list_name: str = event["list_name"]
    db_id: int = event["db_id"]
    new_caption: str = event["new_caption"]

    logger.info(
        "update_list_film_caption_handler curator=%s list_name=%s db_id=%d",
        curator, list_name, db_id,
    )

    s3 = get_s3_client()
    lists_key = f"{FILM_LISTS_BASE_PREFIX}/{curator}/{FILM_LISTS_FILENAME}"
    film_lists = download_json_from_s3(s3, S3_BUCKET, lists_key)

    # Find target list
    target_list = None
    for fl in film_lists:
        if fl["list_name"] == list_name:
            target_list = fl
            break

    if target_list is None:
        raise ValueError(f"List '{list_name}' not found for curator '{curator}'")

    # Find the film
    updated = False
    for film in target_list["list_films"]:
        if film["db_id"] == db_id:
            film["list_film_caption"] = new_caption
            updated = True
            break

    if not updated:
        raise ValueError(f"Film with db_id={db_id} not found in list '{list_name}'")

    upload_dict_to_s3(s3, S3_BUCKET, lists_key, film_lists)

    return {
        "status": "ok",
        "curator": curator,
        "list_name": list_name,
        "db_id": db_id,
        "new_caption": new_caption,
        "output_uri": f"s3://{S3_BUCKET}/{lists_key}",
    }
