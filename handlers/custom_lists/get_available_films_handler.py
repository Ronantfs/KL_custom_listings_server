"""
Return a compact summary of films in pan_cinema_listings.json.

Used by the UI film picker so users can search and select films
to add to a custom list without needing to know db_ids up front.

Accepts optional start_date / end_date (YYYY-MM-DD).  When provided,
only films with at least one showing date inside the range are returned.
Films without a title in _additional_info are always excluded.
"""

import logging
from typing import Dict, Any, Optional, List

from core.s3 import get_s3_client, download_json_from_s3
from core.types.film_listings import PanCinemaCleanedCompactedListings
from config import S3_BUCKET, PAN_CINEMA_LISTINGS_KEY

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _film_has_date_in_range(
    cinema_listings: Dict[str, Any],
    start_date: str,
    end_date: str,
) -> bool:
    """Return True if any showing date falls within [start_date, end_date]."""
    for listing in cinema_listings.values():
        when_list: List[Dict[str, Any]] = listing.get("when", [])
        if not isinstance(when_list, list):
            continue
        for entry in when_list:
            d = entry.get("date", "")
            if isinstance(d, str) and start_date <= d <= end_date:
                return True
    return False


def get_available_films_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    logger.info("get_available_films_handler")

    start_date: Optional[str] = event.get("start_date")
    end_date: Optional[str] = event.get("end_date")

    s3 = get_s3_client()
    pan_listings: PanCinemaCleanedCompactedListings = download_json_from_s3(
        s3, S3_BUCKET, PAN_CINEMA_LISTINGS_KEY
    )

    films: Dict[str, Dict[str, Any]] = {}
    skipped_no_title = 0
    skipped_out_of_range = 0

    for db_id_str, cinema_listings in pan_listings.items():
        # --- resolve title from _additional_info only ---
        title: Optional[str] = None
        directors = None
        year = None

        for listing in cinema_listings.values():
            info = listing.get("_additional_info", {})
            if not title and info.get("title"):
                title = info["title"]
            if not directors and info.get("directors"):
                directors = info["directors"]
            if not year and info.get("year"):
                year = info["year"]

        # Skip films without a proper title
        if not title:
            skipped_no_title += 1
            continue

        # Date-range filter (when dates provided)
        if start_date and end_date:
            if not _film_has_date_in_range(cinema_listings, start_date, end_date):
                skipped_out_of_range += 1
                continue

        # Ensure directors is always a list of strings
        if isinstance(directors, str):
            directors = [directors]
        elif not isinstance(directors, list):
            directors = []

        films[db_id_str] = {
            "title": title,
            "directors": directors,
            "year": year,
            "cinema_count": len(cinema_listings),
            "cinemas": list(cinema_listings.keys()),
        }

    logger.info(
        "available_films=%d skipped_no_title=%d skipped_out_of_range=%d",
        len(films), skipped_no_title, skipped_out_of_range,
    )

    return {
        "status": "ok",
        "film_count": len(films),
        "films": films,
    }
