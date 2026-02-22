"""
Types for the custom film lists managed by this service.

S3 layout:
  s3://filmfynder/london/filmLists/{curator}/filmLists.json

Each curator's filmLists.json is a list of CustomList objects.
"""

from typing import List, TypedDict

from core.types.film_listings import CleanMatchedFilmsCinemaListings


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


# The content of each curator's filmLists.json file
CuratorFilmLists = List[CustomList]
