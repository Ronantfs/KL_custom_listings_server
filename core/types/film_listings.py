"""
Types describing film listing data from the upstream pipeline.
These mirror the types in context_types.py and are used when loading
pan_cinema_listings.json.
"""

from typing import List, Dict, Optional, TypedDict


class StructuredDateStrings(TypedDict):
    Weekday: str        # e.g., "Sunday"
    Month: str          # e.g., "May"
    day_str: str        # e.g., "5th"


class Listing_When_Date(TypedDict):
    date: str           # Format: YYYY-MM-DD
    structured_date_strings: StructuredDateStrings
    year: int
    month: int
    day: int
    showtimes: List[str]  # Format: HH:MM


class CleanedCompactListingAdditionalInfo(TypedDict, total=False):
    title: Optional[str]
    directors: Optional[List[str]]
    cast: Optional[List[str]]
    countries: Optional[List[str]]
    year: Optional[int]
    runtime_mins: Optional[int]
    screening_medium: Optional[str]
    age_rating: Optional[int]
    db_id: Optional[int]
    original_raw_titles: List[str]


class CleanedCompactListing(TypedDict):
    description: str
    screen: Optional[str]
    screeningType: str
    url: Optional[str]
    when: List[Listing_When_Date]
    image_to_download: Optional[str]
    isImageGood: bool
    s3ImageURL: str
    _additional_info: CleanedCompactListingAdditionalInfo


# str keys are cinema names
CleanMatchedFilmsCinemaListings = dict[str, CleanedCompactListing]

# int keys are db_ids -> cinema_name -> listing
PanCinemaCleanedCompactedListings = dict[int, CleanMatchedFilmsCinemaListings]
