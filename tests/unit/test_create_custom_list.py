"""
Unit tests for create_custom_list_handler.

All S3 calls are mocked — these tests only exercise payload validation
and the handler's return shape on success.
"""

import json
import pathlib
from unittest.mock import patch, MagicMock

import pytest

from handlers.custom_lists.create_custom_list_handler import create_custom_list_handler

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "create_custom_list"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


# ── helpers to mock S3 ──────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _mock_s3():
    """Patch S3 so no real AWS calls are made."""
    with (
        patch("handlers.custom_lists.create_custom_list_handler.get_s3_client") as mock_client,
        patch("handlers.custom_lists.create_custom_list_handler.download_json_from_s3") as mock_download,
        patch("handlers.custom_lists.create_custom_list_handler.upload_dict_to_s3") as mock_upload,
    ):
        mock_client.return_value = MagicMock()
        mock_download.side_effect = FileNotFoundError  # fresh curator, no existing lists
        mock_upload.return_value = None
        yield {
            "client": mock_client,
            "download": mock_download,
            "upload": mock_upload,
        }


# ── happy path ──────────────────────────────────────────────────────


class TestCreateCustomListValid:
    def test_valid_payload_returns_ok(self):
        payload = _load_fixture("create_custom_list_valid.json")
        result = create_custom_list_handler(payload)

        assert result["status"] == "ok"
        assert result["curator"] == "TEST_CURATOR"
        assert result["list_name"] == "Best of 2026"
        assert result["lists_total"] == 1

    def test_valid_payload_uploads_to_s3(self, _mock_s3):
        payload = _load_fixture("create_custom_list_valid.json")
        create_custom_list_handler(payload)

        _mock_s3["upload"].assert_called_once()
        uploaded_data = _mock_s3["upload"].call_args[0][3]
        assert len(uploaded_data) == 1
        assert uploaded_data[0]["list_curator"] == "TEST_CURATOR"
        assert uploaded_data[0]["list_films"] == []


# ── missing fields ──────────────────────────────────────────────────


class TestCreateCustomListMissingFields:
    def test_missing_curator(self):
        payload = _load_fixture("create_custom_list_missing_curator.json")
        with pytest.raises(ValueError, match="curator"):
            create_custom_list_handler(payload)

    def test_missing_list_name(self):
        payload = _load_fixture("create_custom_list_missing_list_name.json")
        with pytest.raises(ValueError, match="list_name"):
            create_custom_list_handler(payload)

    def test_missing_all_fields(self):
        payload = _load_fixture("create_custom_list_missing_all_fields.json")
        with pytest.raises(ValueError, match="Missing required fields"):
            create_custom_list_handler(payload)

    def test_empty_caption_treated_as_missing(self):
        payload = _load_fixture("create_custom_list_empty_caption.json")
        with pytest.raises(ValueError, match="list_caption"):
            create_custom_list_handler(payload)


# ── invalid date formats ────────────────────────────────────────────


class TestCreateCustomListBadDates:
    def test_bad_start_date_format(self):
        payload = _load_fixture("create_custom_list_bad_start_date.json")
        with pytest.raises(ValueError, match="start_date"):
            create_custom_list_handler(payload)

    def test_bad_end_date_format(self):
        payload = _load_fixture("create_custom_list_bad_end_date.json")
        with pytest.raises(ValueError, match="end_date"):
            create_custom_list_handler(payload)
