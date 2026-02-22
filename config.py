"""
Service configuration for KL Custom Listings Server.
Fill in all required values before deploying.
"""

# --- AWS ---
AWS_REGION = "eu-north-1"

# --- S3 Bucket & Paths ---
S3_BUCKET = "filmfynder"
# Base prefix under which curator folders live
# e.g. s3://filmfynder/london/filmLists/{curator}/filmLists.json
FILM_LISTS_BASE_PREFIX = "london/filmLists"
# Filename stored inside each curator folder
FILM_LISTS_FILENAME = "filmLists.json"

# Pan-cinema listings (source of truth for film data)
# s3://filmfynder/london/cinema-listings/all/pan_cinema_listings.json
PAN_CINEMA_LISTINGS_KEY = "london/cinema-listings/all/pan_cinema_listings.json"

# --- Lambda ---
LAMBDA_FUNCTION_NAME = "kl_custom_listings"
LAMBDA_URL = "https://b62gakukdi4hlmmcmhx533az3y0fgpqs.lambda-url.eu-north-1.on.aws/"
