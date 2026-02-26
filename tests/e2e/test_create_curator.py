"""
E2E tests for create_curator_handler.

These tests make real S3 calls.
Requires valid AWS credentials (SSO login).
Run with:  pytest tests/e2e/test_create_curator.py -v
"""

import json
import pathlib

import pytest

from handlers.custom_lists.create_curator_handler import create_curator_handler
from core.s3 import get_s3_client, download_json_from_s3
from config import S3_BUCKET, FILM_LISTS_BASE_PREFIX, FILM_LISTS_FILENAME

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "create_curator"

TEST_CURATOR = "e2e_test_curator_tmp"
S3_KEY = f"{FILM_LISTS_BASE_PREFIX}/{TEST_CURATOR}/{FILM_LISTS_FILENAME}"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def _delete_curator_s3():
    """Remove the test curator's filmLists.json from S3."""
    try:
        s3 = get_s3_client()
        s3.delete_object(Bucket=S3_BUCKET, Key=S3_KEY)
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _cleanup():
    """Ensure test curator is removed before and after each test."""
    _delete_curator_s3()
    yield
    _delete_curator_s3()


# ── e2e: create curator ─────────────────────────────────────────────


class TestCreateCuratorE2E:
    def test_create_curator_writes_empty_list_to_s3(self):
        payload = _load_fixture("create_curator_e2e_valid.json")
        result = create_curator_handler(payload)

        assert result["status"] == "ok"
        assert result["curator"] == TEST_CURATOR

        # Verify an empty list was written to S3
        s3 = get_s3_client()
        data = download_json_from_s3(s3, S3_BUCKET, S3_KEY)
        assert data == []

    def test_create_duplicate_curator_raises(self):
        payload = _load_fixture("create_curator_e2e_valid.json")

        # First call succeeds
        create_curator_handler(payload)

        # Second call should raise
        with pytest.raises(ValueError, match="already exists"):
            create_curator_handler(payload)
