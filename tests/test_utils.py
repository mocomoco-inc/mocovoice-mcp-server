import pytest
from pathlib import Path
from unittest.mock import MagicMock

from datetime import datetime
from zoneinfo import ZoneInfo

from moco_voice_mcp.utils import is_path_allowed, validate_file, extract_transcriptions
from moco_voice_mcp.constant import MAX_FILE_SIZE


@pytest.fixture
def sample_allowed_dir(tmp_path):
    """Creates an allowed directory with a sample file inside."""
    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()
    file_inside = allowed_dir / "test.wav"
    file_inside.write_text("sample data")
    return allowed_dir, file_inside


@pytest.fixture
def disallowed_file(tmp_path):
    """Creates a file outside any allowed directory."""
    other_dir = tmp_path / "disallowed"
    other_dir.mkdir()
    file_outside = other_dir / "test.wav"
    file_outside.write_text("unauthorized data")
    return file_outside


def test_is_path_allowed_inside_allowed_dir(sample_allowed_dir):
    allowed_dir, file_inside = sample_allowed_dir
    assert is_path_allowed(file_inside, [allowed_dir]) is True


def test_is_path_allowed_outside_allowed_dir(sample_allowed_dir, disallowed_file):
    allowed_dir, _ = sample_allowed_dir
    assert is_path_allowed(disallowed_file, [allowed_dir]) is False


def test_is_path_allowed_raises():
    class BadPath:
        def resolve(self):
            raise OSError("resolve failed")

    assert is_path_allowed(BadPath(), []) is False  # type: ignore


# ----------------------------
# validate_file
# ----------------------------


def test_validate_file_success(tmp_path, monkeypatch):
    file = tmp_path / "valid.wav"
    file.write_bytes(b"valid data")

    monkeypatch.setitem(
        __import__("moco_voice_mcp.utils").utils.SUPPORT_MEDIA_CONTENT_TYPES,
        ".wav",
        "audio/wav",
    )

    valid, msg = validate_file(file)
    assert valid is True
    assert msg == ""


def test_validate_file_not_exists(tmp_path):
    file = tmp_path / "notfound.wav"
    valid, msg = validate_file(file)
    assert not valid
    assert "存在しません" in msg


def test_validate_file_is_directory(tmp_path):
    directory = tmp_path / "some_dir"
    directory.mkdir()
    valid, msg = validate_file(directory)
    assert not valid
    assert "ファイルではありません" in msg


def test_validate_file_too_large(monkeypatch, tmp_path):
    file = tmp_path / "huge.wav"
    file.write_bytes(b"abc")

    real_stat = file.stat()

    def fake_stat(self):
        if self == file:
            mock_stat = MagicMock()
            mock_stat.st_size = MAX_FILE_SIZE + 1
            mock_stat.st_mode = real_stat.st_mode
            return mock_stat
        return Path.stat(self)

    monkeypatch.setattr(Path, "stat", fake_stat)

    ok, msg = validate_file(file)
    assert not ok
    assert "ファイルサイズである3GBを超えています" in msg


def test_validate_file_empty(tmp_path, monkeypatch):
    file = tmp_path / "empty.wav"
    file.write_bytes(b"")

    monkeypatch.setitem(
        __import__("moco_voice_mcp.utils").utils.SUPPORT_MEDIA_CONTENT_TYPES,
        ".wav",
        "audio/wav",
    )

    valid, msg = validate_file(file)
    assert not valid
    assert "空のファイル" in msg


def test_validate_file_unsupported_type(tmp_path):
    file = tmp_path / "file.unsupported"
    file.write_bytes(b"abc")
    valid, msg = validate_file(file)
    assert not valid
    assert "サポートされていないファイル形式" in msg


# ----------------------------
# extract_transcriptions
# ----------------------------


def test_extract_transcriptions_formats_correctly():
    jst = ZoneInfo("Asia/Tokyo")
    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=jst).isoformat()

    input_data = [
        {
            "transcription_id": "abc123",
            "transcription_path": "https://example.com/audio.wav",
            "status": "completed",
            "created_at": now,
            "name": "example.wav",
        }
    ]

    output = extract_transcriptions(input_data)
    assert isinstance(output, list)
    assert output[0]["書き起こしID"] == "abc123"
    assert output[0]["ステータス"] == "completed"
    assert output[0]["作成日"] == "2024/01/01 12:00"
    assert output[0]["音声データの名前"] == "example.wav"


def test_extract_transcriptions_naive_datetime_handling():
    # naive datetime (tzinfoなし)
    naive = "2024-01-01T12:00:00"
    input_data = [
        {
            "transcription_id": "naive123",
            "transcription_path": "/path",
            "status": "done",
            "created_at": naive,
            "name": "naive.wav",
        }
    ]

    output = extract_transcriptions(input_data)
    assert output[0]["作成日"] == "2024/01/01 12:00"
