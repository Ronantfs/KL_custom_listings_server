"""
E2E tests for get_curators_handler.

These tests make real S3 calls.
Requires valid AWS credentials (SSO login).
Run with:  pytest tests/e2e/ -v
"""

import json
import pathlib

import pytest

from handlers.custom_lists.create_custom_list_handler import create_custom_list_handler
from handlers.custom_lists.delete_list_handler import delete_list_handler
from handlers.custom_lists.get_curators_handler import get_curators_handler

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "get_curators"

TEST_CURATOR = "TEST_CURATOR"
TEST_LIST_NAME = "E2E Curators Test List"


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


# ── e2e: get curators ───────────────────────────────────────────────


class TestGetCuratorsE2E:
    def test_returns_curators_including_test_curator(self):
        create_custom_list_handler(_load_fixture("get_curators_setup.json"))

        result = get_curators_handler({})

        assert result["status"] == "ok"
        assert isinstance(result["curators"], list)
        assert TEST_CURATOR in result["curators"]

    def test_curators_are_strings(self):
        create_custom_list_handler(_load_fixture("get_curators_setup.json"))

        result = get_curators_handler({})

        for curator in result["curators"]:
            assert isinstance(curator, str)
