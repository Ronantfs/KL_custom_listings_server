"""
Types for the custom film lists managed by this service.

S3 layout:
  s3://filmfynder/london/filmLists/{curator}/filmLists.json

Each curator's filmLists.json is a JSON array of CustomList objects:

    CuratorFilmLists = List[CustomList]

Full structure:

    [                                          # CuratorFilmLists
      {                                        # CustomList
        "list_curator": "kinologue",
        "list_name": "March Picks",
        "list_caption": "Our favourite films this month",
        "start_date": "2025-03-01",            # YYYY-MM-DD
        "end_date": "2025-03-31",              # YYYY-MM-DD
        "list_films": [                        # List[ListFilm]
          {                                    # ListFilm
            "db_id": 6114,
            "list_film_caption": "A gothic masterpiece",
            "cinema_listings": {               # Dict[str, CleanedCompactListing]
              "prince_charles": {              # CleanedCompactListing
                "description": "...",
                "screen": "Screen 1",
                "screeningType": "35mm",
                "url": "https://...",
                "when": [                      # List[Listing_When_Date]
                  {
                    "date": "2025-03-15",
                    "structured_date_strings": {
                      "Weekday": "Saturday",
                      "Month": "March",
                      "day_str": "15th"
                    },
                    "year": 2025,
                    "month": 3,
                    "day": 15,
                    "showtimes": ["14:00", "19:30"]
                  }
                ],
                "image_to_download": null,
                "isImageGood": true,
                "s3ImageURL": "https://...",
                "_additional_info": {          # CleanedCompactListingAdditionalInfo
                  "title": "Bram Stoker's Dracula",
                  "directors": ["Francis Ford Coppola"],
                  "year": 1992,
                  "runtime_mins": 128,
                  "db_id": 6114
                }
              }
            }
          }
        ]
      }
    ]
"""

import logging

from typing import Any, Dict, List, Optional, TypedDict

from core.types.film_listings import CleanMatchedFilmsCinemaListings

CUSTOM_LIST_REQUIRED_KEYS = {"list_curator", "list_name", "list_caption", "start_date", "end_date", "list_films"}


class ListFilm(TypedDict):
    """A single film in a custom list, keyed by db_id.

    cinema_listings maps cinema snake_case name (e.g. "prince_charles")
    to the full CleanedCompactListing from pan_cinema_listings.json.
    """
    db_id: int
    cinema_listings: CleanMatchedFilmsCinemaListings
    list_film_caption: str


class CustomList(TypedDict):
    """One curated list within a curator's filmLists.json."""
    list_curator: str
    list_name: str
    list_caption: str
    start_date: str   # YYYY-MM-DD
    end_date: str     # YYYY-MM-DD
    list_films: List[ListFilm]


class CinemaShowing(TypedDict):
    """A single date + showtimes pair, used in the get_available_films response."""
    date: str           # YYYY-MM-DD
    showtimes: List[str]  # HH:MM


class AvailableFilmSummary(TypedDict):
    """Compact film summary returned by get_available_films_handler.

    cinema_showings maps cinema name to a list of CinemaShowing,
    giving dates and times the film is showing at each cinema.
    A cinema with an empty list means the film is listed there
    but no screening dates were found.
    """
    title: str
    directors: List[str]
    year: Optional[int]
    cinema_count: int
    cinemas: List[str]
    cinema_showings: Dict[str, List[CinemaShowing]]


# The root type of each curator's filmLists.json file
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
