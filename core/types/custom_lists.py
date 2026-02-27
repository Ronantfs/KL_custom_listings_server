"""
Types for the custom film lists managed by this service.

S3 layout:
  s3://filmfynder/london/filmLists/{curator}/filmLists.json

Each curator's filmLists.json is a list of CustomList objects.
"""

import logging

from typing import Any, Dict, List, Optional, TypedDict

from core.types.film_listings import CleanMatchedFilmsCinemaListings

CUSTOM_LIST_REQUIRED_KEYS = {"list_curator", "list_name", "list_caption", "start_date", "end_date", "list_films"}


class ListFilm(TypedDict):
    db_id: int
    cinema_listings: CleanMatchedFilmsCinemaListings  # cinema_name -> CleanedCompactListing
    list_film_caption: str


class CustomList(TypedDict):
    list_curator: str
    list_name: str
    list_caption: str
    start_date: str   # YYYY-MM-DD
    end_date: str     # YYYY-MM-DD
    list_films: List[ListFilm]


class CinemaShowing(TypedDict):
    date: str           # YYYY-MM-DD
    showtimes: List[str]  # HH:MM


class AvailableFilmSummary(TypedDict):
    title: str
    directors: List[str]
    year: Optional[int]
    cinema_count: int
    cinemas: List[str]
    cinema_showings: Dict[str, List[CinemaShowing]]


# The content of each curator's filmLists.json file
CuratorFilmLists = List[CustomList]


def validate_curator_film_lists(data: Any, curator: str) -> CuratorFilmLists:
    """Validate that data from S3 matches the CuratorFilmLists shape.

    Returns the validated list. If the file is empty or a non-list
    placeholder (e.g. ``{}``), returns ``[]`` so callers can proceed
    normally.  Raises ValueError only when the file contains real
    entries that are malformed.
    """
    if not isinstance(data, list):
        if isinstance(data, dict) and len(data) == 0:
            logging.getLogger(__name__).warning(
                "filmLists.json for curator '%s' is an empty object, treating as empty list", curator
            )
            return []
        raise ValueError(
            f"Corrupt filmLists.json for curator '{curator}': "
            f"expected a JSON array, got {type(data).__name__}"
        )

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(
                f"Corrupt filmLists.json for curator '{curator}': "
                f"entry {i} is {type(item).__name__}, expected an object"
            )
        missing = CUSTOM_LIST_REQUIRED_KEYS - item.keys()
        if missing:
            raise ValueError(
                f"Corrupt filmLists.json for curator '{curator}': "
                f"entry {i} ('{item.get('list_name', '?')}') is missing keys: {', '.join(sorted(missing))}"
            )
        if not isinstance(item["list_films"], list):
            raise ValueError(
                f"Corrupt filmLists.json for curator '{curator}': "
                f"entry {i} ('{item['list_name']}') list_films is {type(item['list_films']).__name__}, expected an array"
            )

    return data
