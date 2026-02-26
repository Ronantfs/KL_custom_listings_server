"""
Unit tests for create_curator_handler.

All S3 calls are mocked — these tests exercise payload validation,
name normalisation, duplicate detection, and the return shape on success.
"""

import json
import pathlib
from unittest.mock import patch, MagicMock

import pytest

from handlers.custom_lists.create_curator_handler import create_curator_handler

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "create_curator"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


# ── helpers to mock S3 ──────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _mock_s3():
    """Patch S3 so no real AWS calls are made."""
    with (
        patch("handlers.custom_lists.create_curator_handler.get_s3_client") as mock_client,
        patch("handlers.custom_lists.create_curator_handler.download_json_from_s3") as mock_download,
        patch("handlers.custom_lists.create_curator_handler.upload_dict_to_s3") as mock_upload,
    ):
        mock_client.return_value = MagicMock()
        mock_download.side_effect = FileNotFoundError  # curator doesn't exist yet
        mock_upload.return_value = None
        yield {
            "client": mock_client,
            "download": mock_download,
            "upload": mock_upload,
        }


# ── happy path ──────────────────────────────────────────────────────


class TestCreateCuratorValid:
    def test_valid_payload_returns_ok(self):
        payload = _load_fixture("create_curator_valid.json")
        result = create_curator_handler(payload)

        assert result["status"] == "ok"
        assert result["curator"] == "test_new_curator"
        assert "output_uri" in result

    def test_valid_payload_uploads_empty_list(self, _mock_s3):
        payload = _load_fixture("create_curator_valid.json")
        create_curator_handler(payload)

        _mock_s3["upload"].assert_called_once()
        uploaded_data = _mock_s3["upload"].call_args[0][3]
        assert uploaded_data == []

    def test_s3_key_contains_curator_name(self, _mock_s3):
        payload = _load_fixture("create_curator_valid.json")
        create_curator_handler(payload)

        s3_key = _mock_s3["upload"].call_args[0][2]
        assert "test_new_curator" in s3_key
        assert s3_key.endswith("filmLists.json")

    def test_hyphens_allowed_in_name(self):
        payload = _load_fixture("create_curator_with_hyphens.json")
        result = create_curator_handler(payload)

        assert result["status"] == "ok"
        assert result["curator"] == "my-cool-curator"


# ── name normalisation ──────────────────────────────────────────────


class TestCreateCuratorNormalisation:
    def test_uppercase_normalised_to_lowercase(self):
        payload = _load_fixture("create_curator_uppercase.json")
        result = create_curator_handler(payload)

        assert result["status"] == "ok"
        assert result["curator"] == "my_curator"

    def test_whitespace_stripped(self):
        payload = _load_fixture("create_curator_uppercase.json")
        result = create_curator_handler(payload)

        # "  My_Curator  " → "my_curator"
        assert result["curator"] == "my_curator"


# ── missing / empty field ───────────────────────────────────────────


class TestCreateCuratorMissingField:
    def test_missing_curator_field(self):
        payload = _load_fixture("create_curator_missing_curator.json")
        with pytest.raises(ValueError, match="Missing required field"):
            create_curator_handler(payload)

    def test_empty_curator_string(self):
        payload = _load_fixture("create_curator_empty_curator.json")
        with pytest.raises(ValueError, match="Missing required field"):
            create_curator_handler(payload)


# ── invalid name format ─────────────────────────────────────────────


class TestCreateCuratorInvalidName:
    def test_invalid_characters_rejected(self):
        payload = _load_fixture("create_curator_invalid_chars.json")
        with pytest.raises(ValueError, match="Invalid curator name"):
            create_curator_handler(payload)

    def test_too_short_name_rejected(self):
        payload = _load_fixture("create_curator_too_short.json")
        with pytest.raises(ValueError, match="Invalid curator name"):
            create_curator_handler(payload)

    def test_spaces_in_name_rejected(self):
        # After strip+lower: "bad curator name!" contains spaces → invalid
        payload = _load_fixture("create_curator_invalid_chars.json")
        with pytest.raises(ValueError, match="Invalid curator name"):
            create_curator_handler(payload)


# ── duplicate detection ─────────────────────────────────────────────


class TestCreateCuratorDuplicate:
    def test_existing_curator_raises(self, _mock_s3):
        # Make download succeed → curator already exists
        _mock_s3["download"].side_effect = None
        _mock_s3["download"].return_value = []

        payload = _load_fixture("create_curator_valid.json")
        with pytest.raises(ValueError, match="already exists"):
            create_curator_handler(payload)

    def test_no_upload_when_duplicate(self, _mock_s3):
        _mock_s3["download"].side_effect = None
        _mock_s3["download"].return_value = []

        payload = _load_fixture("create_curator_valid.json")
        with pytest.raises(ValueError):
            create_curator_handler(payload)

        _mock_s3["upload"].assert_not_called()
