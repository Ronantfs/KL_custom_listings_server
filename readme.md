# KL Custom Listings Server

## Local Install (uv)

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## S3 File Structure

Bucket: `filmfynder`

```
london/
  filmLists/
    {curator}/                          # e.g. "kinologue"
      filmLists.json                    # CuratorFilmLists (List[CustomList])
  cinema-listings/
    all/
      pan_cinema_listings.json          # PanCinemaCleanedCompactedListings
```

### Types

**Server** — `core/types/custom_lists.py`, `core/types/film_listings.py`

| Type | Description |
|------|-------------|
| `CuratorFilmLists` | `List[CustomList]` — root of each curator's `filmLists.json` |
| `CustomList` | `list_curator`, `list_name`, `list_caption`, `start_date`, `end_date`, `list_films: List[ListFilm]` |
| `ListFilm` | `db_id: int`, `cinema_listings: dict[cinema_name, CleanedCompactListing]`, `list_film_caption: str` |
| `PanCinemaCleanedCompactedListings` | `dict[db_id, dict[cinema_name, CleanedCompactListing]]` — source film data |

**UI** — `src/types/customLists.ts`

| Interface | Maps to |
|-----------|---------|
| `CustomList` | Server `CustomList` |
| `ListFilm` | Server `ListFilm` |
| `CinemaListing` | Server `CleanedCompactListing` |
| `GetCuratorsResponse` | `get_curators` handler response |
| `GetCustomListsResponse` | `get_custom_lists` handler response |
| `CreateCustomListResponse` | `create_custom_list` handler response |
| `AssignFilmsResponse` | `assign_films_to_list` handler response |
| `DeleteListResponse` | `delete_list` handler response |

## Build & Deploy (CLI)

All commands run from the `KL_custom_listings_server/` directory.

### Build the Lambda zip

```bash
bash buildDeploy/build_lambda.sh
```

Output: `dist/custom_listings_entrypoint_lambda.zip`

### Deploy to AWS (build + deploy)

```bash
bash buildDeploy/deploy.sh
```

### Deploy only (skip build)

```bash
bash buildDeploy/deploy.sh --skip-build
```

### One-liner: build and deploy

```bash
bash buildDeploy/build_lambda.sh && bash buildDeploy/deploy.sh --skip-build
```

