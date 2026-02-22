"""
Route 3: Assign films to a given custom list.

Payload specifies curator, list_name, and db_ids of films to assign.
Loads pan_cinema_listings.json to get full film data for each db_id,
then stores that data (plus empty caption) in the list.
"""

import logging
from typing import Dict, Any, List

from core.s3 import get_s3_client, download_json_from_s3, upload_dict_to_s3
from config import (
    S3_BUCKET,
    FILM_LISTS_BASE_PREFIX,
    FILM_LISTS_FILENAME,
    PAN_CINEMA_LISTINGS_KEY,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def assign_films_to_list_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    curator: str = event["curator"]
    list_name: str = event["list_name"]
    db_ids: List[int] = event["db_ids"]

    logger.info(
        "assign_films_to_list_handler curator=%s list_name=%s db_ids=%s",
        curator, list_name, db_ids,
    )

    s3 = get_s3_client()

    # Load curator's lists
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

    # Load pan cinema listings
    pan_listings = download_json_from_s3(s3, S3_BUCKET, PAN_CINEMA_LISTINGS_KEY)

    # Already-assigned db_ids (avoid duplicates)
    existing_db_ids = {film["db_id"] for film in target_list["list_films"]}

    added = []
    skipped = []
    not_found = []

    for db_id in db_ids:
        if db_id in existing_db_ids:
            skipped.append(db_id)
            continue

        # pan_listings keys are stringified ints in JSON
        str_id = str(db_id)
        if str_id not in pan_listings:
            not_found.append(db_id)
            continue

        cinema_listings = pan_listings[str_id]

        list_film = {
            "db_id": db_id,
            "cinema_listings": cinema_listings,
            "list_film_caption": "",
        }

        target_list["list_films"].append(list_film)
        existing_db_ids.add(db_id)
        added.append(db_id)

    upload_dict_to_s3(s3, S3_BUCKET, lists_key, film_lists)

    return {
        "status": "ok",
        "curator": curator,
        "list_name": list_name,
        "films_added": added,
        "films_skipped_already_in_list": skipped,
        "films_not_found_in_pan_listings": not_found,
        "total_list_films": len(target_list["list_films"]),
        "output_uri": f"s3://{S3_BUCKET}/{lists_key}",
    }
