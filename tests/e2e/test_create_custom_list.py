"""
E2E tests for create_custom_list_handler.

These tests make real S3 calls using TEST_CURATOR.
Requires valid AWS credentials (SSO login).
Run with:  pytest tests/e2e/ -v
"""

import json
import pathlib

import pytest

from handlers.custom_lists.create_custom_list_handler import create_custom_list_handler
from handlers.custom_lists.delete_list_handler import delete_list_handler
from core.s3 import get_s3_client, download_json_from_s3
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX, FILM_LISTS_FILENAME

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "create_custom_list"

TEST_CURATOR = "TEST_CURATOR"
TEST_LIST_NAME = "E2E Test List"
S3_KEY = f"{FILM_LISTS_BASE_PREFIX}/{TEST_CURATOR}/{FILM_LISTS_FILENAME}"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture(autouse=True)
def _cleanup_test_list():
    """Delete the test list from S3 after each test, if it exists."""
    yield
    try:
        delete_list_handler(
            {"curator": TEST_CURATOR, "list_name": TEST_LIST_NAME}
        )
    except (ValueError, FileNotFoundError, RuntimeError):
        # List wasn't created or already gone — nothing to clean up
        pass


# ── e2e: create list round-trip ─────────────────────────────────────


class TestCreateCustomListE2E:
    def test_create_list_writes_to_s3(self):
        payload = {
            "handler": "create_custom_list",
            "curator": TEST_CURATOR,
            "list_name": TEST_LIST_NAME,
            "list_caption": "E2E test caption",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        }

        result = create_custom_list_handler(payload)

        assert result["status"] == "ok"
        assert result["curator"] == TEST_CURATOR
        assert result["list_name"] == TEST_LIST_NAME

        # Verify the list actually exists in S3
        s3 = get_s3_client()
        data = download_json_from_s3(s3, S3_BUCKET, S3_KEY)
        created = [l for l in data if l["list_name"] == TEST_LIST_NAME]
        assert len(created) == 1
        assert created[0]["list_curator"] == TEST_CURATOR
        assert created[0]["list_caption"] == "E2E test caption"
        assert created[0]["list_films"] == []

    def test_duplicate_list_name_raises(self):
        payload = {
            "handler": "create_custom_list",
            "curator": TEST_CURATOR,
            "list_name": TEST_LIST_NAME,
            "list_caption": "First creation",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        }

        # Create it once
        create_custom_list_handler(payload)

        # Creating again with same name should fail
        with pytest.raises(ValueError, match="already exists"):
            create_custom_list_handler(payload)
