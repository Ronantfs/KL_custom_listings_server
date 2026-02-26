"""
E2E tests for delete_list_handler.

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

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "delete_list"

TEST_CURATOR = "TEST_CURATOR"
TEST_LIST_NAME = "E2E Delete Test List"
S3_KEY = f"{FILM_LISTS_BASE_PREFIX}/{TEST_CURATOR}/{FILM_LISTS_FILENAME}"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def _create_test_list():
    """Create a test list so delete has something to work with."""
    payload = _load_fixture("delete_list_setup.json")
    return create_custom_list_handler(payload)


@pytest.fixture(autouse=True)
def _cleanup_test_list():
    """Delete the test list from S3 after each test, if it exists."""
    yield
    try:
        delete_list_handler(
            {"curator": TEST_CURATOR, "list_name": TEST_LIST_NAME}
        )
    except (ValueError, FileNotFoundError, RuntimeError):
        pass


# ── e2e: delete list ────────────────────────────────────────────────


class TestDeleteListE2E:
    def test_delete_list_removes_from_s3(self):
        _create_test_list()

        result = delete_list_handler(
            _load_fixture("delete_list_valid.json")
        )

        assert result["status"] == "ok"
        assert result["curator"] == TEST_CURATOR
        assert result["deleted_list"] == TEST_LIST_NAME

        # Verify the list is actually gone from S3
        s3 = get_s3_client()
        try:
            data = download_json_from_s3(s3, S3_BUCKET, S3_KEY)
        except FileNotFoundError:
            data = []
        matching = [fl for fl in data if fl["list_name"] == TEST_LIST_NAME]
        assert len(matching) == 0

    def test_delete_nonexistent_list_raises(self):
        # Ensure TEST_CURATOR has a filmLists.json (create then delete the test list)
        _create_test_list()
        delete_list_handler(
            {"curator": TEST_CURATOR, "list_name": TEST_LIST_NAME}
        )

        with pytest.raises(ValueError, match="not found"):
            delete_list_handler(
                {"curator": TEST_CURATOR, "list_name": "NonExistent List 99999"}
            )
