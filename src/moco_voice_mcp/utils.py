import uuid
from pathlib import Path
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from moco_voice_mcp.constant import (
    MOCOVOICE_API_KEY,
    MAX_FILE_SIZE,
    SUPPORT_MEDIA_CONTENT_TYPES,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_header() -> dict[str, str]:
    return {"X-API-KEY": MOCOVOICE_API_KEY}


def is_valid_uuid(transcription_id) -> bool:
    try:
        uuid.UUID(transcription_id)
    except ValueError:
        return False
    return True


def is_path_allowed(path: Path, allowed_dirs: list[Path]) -> bool:
    try:
        resolved_path = path.resolve()
        resolved_parents = set(resolved_path.parents)
        resolved_parents.add(resolved_path)

        for allowed in allowed_dirs:
            resolved_allowed = allowed.resolve()
            if resolved_allowed in resolved_parents:
                return True

        return False
    except (OSError, ValueError) as e:
        logger.warning(f"is_path_allowed, TAREGT_PATH: {path}, ERROR CODE: {e}")
        return False


def validate_file(file_path: Path) -> tuple[bool, str]:
    if not file_path.exists():
        return False, "指定されたファイルは存在しません。ファイルパスをご確認ください"

    if not file_path.is_file():
        return (
            False,
            "指定されたパスはファイルではありません。ファイルパスをご確認ください",
        )

    try:
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            return (
                False,
                "指定されたファイルはmocoVoiceが対応しているファイルサイズである3GBを超えています",
            )

        if file_size == 0:
            return (
                False,
                "指定されたファイルは空のファイルです。ファイル内容をご確認ください",
            )
    except OSError as e:
        logger.error(f"validate_file, FILE: {file_path}, ERROR: {e}")
        return False, "ファイル情報の取得に失敗しました。ファイル内容をご確認ください"

    if file_path.suffix.lower() not in SUPPORT_MEDIA_CONTENT_TYPES.keys():
        return False, "mocoVoiceではサポートされていないファイル形式です"

    return True, ""


def extract_transcriptions(transcriptions: list[dict]) -> list[dict]:
    data = []
    jst = ZoneInfo("Asia/Tokyo")
    for transcription in transcriptions:
        dt = datetime.fromisoformat(transcription["created_at"])
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=jst)
        else:
            dt = dt.astimezone(jst)

        created_at_str = dt.strftime("%Y/%m/%d %H:%M")
        data.append(
            {
                "書き起こしID": transcription["transcription_id"],
                "書き起こしデータの取得URL": transcription["transcription_path"],
                "ステータス": transcription["status"],
                "話者数": transcription["num_speakers"],
                "作成日": created_at_str,
                "音声データの名前": transcription["name"],
            }
        )

    return data
