"""
Route 0: Get list of curators who have filmLists.json files.

Lists all "folders" (common prefixes) under:
  s3://filmfynder/london/filmLists/

Returns curator names (e.g. ["kinologue", "bfi", ...]).
"""

import logging
from typing import Dict, Any

from core.s3 import get_s3_client
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_curators_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    logger.info("get_curators_handler called")

    s3 = get_s3_client()

    prefix = f"{FILM_LISTS_BASE_PREFIX}/"
    response = s3.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=prefix,
        Delimiter="/",
    )

    curators = []
    for cp in response.get("CommonPrefixes", []):
        # cp["Prefix"] looks like "london/filmLists/kinologue/"
        curator_name = cp["Prefix"].rstrip("/").split("/")[-1]
        curators.append(curator_name)

    logger.info("Found %d curators", len(curators))

    return {
        "status": "ok",
        "curators": curators,
    }
