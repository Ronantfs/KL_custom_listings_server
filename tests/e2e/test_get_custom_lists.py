"""
E2E tests for get_custom_lists_handler.

These tests make real S3 calls using TEST_CURATOR.
Requires valid AWS credentials (SSO login).
Run with:  pytest tests/e2e/ -v
"""

import json
import pathlib

import pytest

from handlers.custom_lists.create_custom_list_handler import create_custom_list_handler
from handlers.custom_lists.delete_list_handler import delete_list_handler
from handlers.custom_lists.get_custom_lists_handler import get_custom_lists_handler

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "get_custom_lists"

TEST_CURATOR = "TEST_CURATOR"
TEST_LIST_NAME = "E2E Get Lists Test"


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
        pass


# ── e2e: get custom lists ───────────────────────────────────────────


class TestGetCustomListsE2E:
    def test_returns_empty_for_unknown_curator(self):
        result = get_custom_lists_handler({
            "curator": "NONEXISTENT_CURATOR_E2E_99999",
        })

        assert result["status"] == "ok"
        assert result["lists_count"] == 0
        assert result["film_lists"] == []

    def test_returns_created_list(self):
        create_custom_list_handler(_load_fixture("get_custom_lists_setup.json"))

        result = get_custom_lists_handler({"curator": TEST_CURATOR})

        assert result["status"] == "ok"
        assert result["lists_count"] >= 1

        matching = [fl for fl in result["film_lists"] if fl["list_name"] == TEST_LIST_NAME]
        assert len(matching) == 1
        assert matching[0]["list_curator"] == TEST_CURATOR
        assert matching[0]["list_caption"] == "List created for get_custom_lists e2e test"

    def test_returned_lists_have_expected_keys(self):
        create_custom_list_handler(_load_fixture("get_custom_lists_setup.json"))

        result = get_custom_lists_handler({"curator": TEST_CURATOR})

        matching = [fl for fl in result["film_lists"] if fl["list_name"] == TEST_LIST_NAME]
        assert len(matching) == 1

        expected_keys = {"list_curator", "list_name", "list_caption", "start_date", "end_date", "list_films"}
        assert expected_keys.issubset(matching[0].keys())
