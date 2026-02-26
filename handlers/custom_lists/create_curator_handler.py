"""
Create a new curator.

Validates the curator name, checks it doesn't already exist,
then writes an empty filmLists.json to establish the curator's folder.
"""

import logging
import re
from typing import Dict, Any

from core.s3 import get_s3_client, download_json_from_s3, upload_dict_to_s3
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX, FILM_LISTS_FILENAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Allow lowercase letters, digits, underscores, hyphens. 2-60 chars.
CURATOR_NAME_PATTERN = re.compile(r"^[a-z0-9_-]{2,60}$")


def create_curator_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    curator = (event.get("curator") or "").strip().lower()

    if not curator:
        raise ValueError("Missing required field: curator")

    if not CURATOR_NAME_PATTERN.match(curator):
        raise ValueError(
            f"Invalid curator name '{curator}'. "
            "Must be 2-60 characters using only lowercase letters, digits, underscores, or hyphens."
        )

    logger.info("create_curator_handler curator=%s", curator)

    s3 = get_s3_client()
    key = f"{FILM_LISTS_BASE_PREFIX}/{curator}/{FILM_LISTS_FILENAME}"

    # Check if curator already exists
    try:
        download_json_from_s3(s3, S3_BUCKET, key)
        raise ValueError(f"Curator '{curator}' already exists")
    except FileNotFoundError:
        pass  # Expected — curator doesn't exist yet

    # Create empty filmLists.json
    upload_dict_to_s3(s3, S3_BUCKET, key, [])

    return {
        "status": "ok",
        "curator": curator,
        "output_uri": f"s3://{S3_BUCKET}/{key}",
    }
