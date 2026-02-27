"""
Return a compact summary of all films in pan_cinema_listings.json.

Used by the UI film picker so users can search and select films
to add to a custom list without needing to know db_ids up front.
Films without a title in _additional_info are excluded.
"""

import logging
from typing import Dict, Any, Optional, List

from core.s3 import get_s3_client, download_json_from_s3
from core.types.film_listings import PanCinemaCleanedCompactedListings
from core.types.custom_lists import AvailableFilmSummary, CinemaShowing
from config import S3_BUCKET, PAN_CINEMA_LISTINGS_KEY

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_available_films_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    logger.info("get_available_films_handler")

    s3 = get_s3_client()
    pan_listings: PanCinemaCleanedCompactedListings = download_json_from_s3(
        s3, S3_BUCKET, PAN_CINEMA_LISTINGS_KEY
    )

    films: Dict[str, AvailableFilmSummary] = {}
    skipped_no_title = 0

    for db_id_str, cinema_listings in pan_listings.items():
        title: Optional[str] = None
        directors: Optional[List[str]] = None
        year: Optional[int] = None

        for listing in cinema_listings.values():
            info = listing.get("_additional_info", {})
            if not title and info.get("title"):
                title = info["title"]
            if not directors:
                raw_dirs = info.get("directors")
                if isinstance(raw_dirs, list):
                    directors = raw_dirs
                elif isinstance(raw_dirs, str):
                    directors = [raw_dirs]
            if not year and info.get("year"):
                year = info["year"]

        # Skip films without a proper title
        if not title:
            skipped_no_title += 1
            continue

        # Ensure directors is always a list of strings
        if directors is None:
            directors = []

        # Build per-cinema showings (always include cinema even if no dates)
        cinema_showings: Dict[str, List[CinemaShowing]] = {}
        for cinema_name, listing in cinema_listings.items():
            when_list = listing.get("when", [])
            dates: List[CinemaShowing] = []
            if isinstance(when_list, list):
                for entry in when_list:
                    d = entry.get("date", "")
                    if isinstance(d, str) and d:
                        dates.append(CinemaShowing(
                            date=d,
                            showtimes=entry.get("showtimes", []),
                        ))
            cinema_showings[cinema_name] = dates

        films[db_id_str] = AvailableFilmSummary(
            title=title,
            directors=directors,
            year=year,
            cinema_count=len(cinema_listings),
            cinemas=list(cinema_listings.keys()),
            cinema_showings=cinema_showings,
        )

    logger.info(
        "available_films=%d skipped_no_title=%d",
        len(films), skipped_no_title,
    )

    return {
        "status": "ok",
        "film_count": len(films),
        "films": films,
    }
