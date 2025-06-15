import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from collections import defaultdict
from textwrap import dedent
from urllib.parse import urljoin
from moco_voice_mcp.api import api_call
from moco_voice_mcp.utils import (
    build_header,
    is_valid_uuid,
    is_path_allowed,
    validate_file,
    extract_transcriptions,
)

from moco_voice_mcp.constant import (
    ALLOWED_DIR,
    MOCOVOICE_API_KEY,
    MOCOVOICE_API_URL,
    SUPPORT_MEDIA_CONTENT_TYPES,
)


mcp = FastMCP("mocoVoice MCP server")


@mcp.tool(name="SHOW_USAGE")
async def show_usage_description() -> str:
    """mocoVoice MCP server の機能説明をする"""
    return dedent("""
    mocoVoice MCP server は発行されたAPIキーを設定することで音声書き起こしを行うことができるMCP Server です
    
    本MCPが提供している機能は下記のとおりです
    
    [SHOW_USAGE]
    mocoVoice MCP server の機能一覧を表示します

    [SHOW_AVAILABLE_FORMATS]
    mocoVoice MCP server が対応している音声・動画ファイル形式を返却します
                  
    [SHOW_AVAILABLE_FILES]
    mocoVoice MCP server が利用できる音声・動画ファイル一覧を返却します
    利用できる音声・動画ファイル一覧は指定されたディレクトリ（フォルダー）配下のみです

    [START_TRANSCRIPTION_JOB]
    指定されたファイルで書き起こしジョブを起動します
    ファイルの指定は絶対パスで行う必要があります

    [SHOW_TRANSCRIPTION_RESULT]
    書き起こしIDを指定して、書き起こし結果を取得して表示します
                  
    [CHECK_TRANSCRIPTION_STATUSES]
    今までの書き起こし一覧を取得します

    ---

    公式サイト: https://www.mocomoco.ai/
    ドキュメント: https://docs.mocomoco.ai/
                  
    免責事項:
    本ツールはMITライセンスに基づき、いかなる保証や公式のサポートを約束するものではありません。
    機能をご確認の上、ご使用の際は自己責任でご利用ください。
    """).strip()


@mcp.tool(name="SHOW_AVAILABLE_FORMATS")
async def show_available_formats() -> str:
    """mocoVoice MCP server が対応している音声・動画ファイル形式を返却する"""
    return dedent("""
    mocoVoice MCP server が対応している音声・動画ファイル形式は下記です
    [音声]
    ".wav", ".mp3", ".m4a", ".caf", ".aiff", ".wma", ".flac", ".ogg", ".aac",
    [動画]
    ".avi", ".mp4", ".rmvb", ".flv", ".mov", ".wm"
    最新の情報はFAQページでご確認ください
    https://docs.mocomoco.ai/faq
    """).strip()


@mcp.tool(name="SHOW_AVAILABLE_FILES")
async def get_files_in_the_target_directory() -> dict[str, list[str]]:
    """mocoVoice MCP server が利用できる音声・動画ファイル一覧を返却します
    mocoVoice API が現在認識できるファイル形式のみが返却されます
    利用できる音声・動画ファイル一覧は指定されたディレクトリ（フォルダー）配下のみです
    """
    result = defaultdict(list)

    for path in ALLOWED_DIR.rglob("*"):
        if path.is_file() and is_path_allowed(path, [ALLOWED_DIR]):
            if path.suffix.lower() in SUPPORT_MEDIA_CONTENT_TYPES.keys():
                result[path.parent].append(path.name)

    return result


@mcp.tool(name="START_TRANSCRIPTION_JOB")
async def start_transcription(path: str, language: str = "ja") -> dict[str, str]:
    """指定されたファイルで書き起こしジョブを起動します
    Args:
        path: 書き起こしを行うファイルパスの名前です
        language: ファイルの言語設定です。デフォルトは `ja` (日本語)

    Returns:
        dict[str, str]: message -> 成功 or エラーメッセージの表示
    """
    file_path = Path(path).expanduser().resolve()
    if not is_path_allowed(file_path, [ALLOWED_DIR]):
        return {
            "message": "与えられたファイルは許可されているディレクトリ(フォルダー)外にあります。フォルダーの設定をご確認ください。"
        }

    valid, message = validate_file(file_path)
    if not valid:
        return {"message": message}

    _, ext = os.path.splitext(file_path)
    basename = os.path.basename(file_path)
    if ext not in SUPPORT_MEDIA_CONTENT_TYPES.keys():
        return {
            "message": "与えられたファイルは対応しているファイル形式ではありません。ファイル形式をご確認ください。"
        }

    headers = {
        "accept": "application/json",
        "X-API-KEY": MOCOVOICE_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {"filename": basename, "language": language}

    url = urljoin(MOCOVOICE_API_URL, "/api/v1/transcriptions/upload")
    data = await api_call(
        lambda client: client.post(url, headers=headers, json=payload)
    )

    upload_url = data["audio_upload_url"]
    transcription_id = data["transcription_id"]
    headers = {
        "Content-Type": SUPPORT_MEDIA_CONTENT_TYPES[ext],
    }

    with open(file_path, "rb") as f:
        content = f.read()

    await api_call(
        lambda client: client.put(upload_url, content=content, headers=headers),
        timeout=3600,
    )

    headers = {
        "accept": "application/json",
        "X-API-KEY": MOCOVOICE_API_KEY,
    }
    url = urljoin(
        MOCOVOICE_API_URL, f"/api/v1/transcriptions/{transcription_id}/transcribe"
    )

    data = await api_call(lambda client: client.post(url, headers=headers, json=""))
    return {"message": "成功しました"}


@mcp.tool(name="CHECK_TRANSCRIPTION_STATUSES")
async def fetch_transcription_status(page: int = 1) -> dict | list[dict]:
    """書き起こしの状態一覧を取得します
    Args:
        page: int
            書き起こし一覧のページングです。デフォルトは一番最新のページになります

    Returns:
        dict[str, str]: 失敗した場合には message -> エラーメッセージで返却されます
        list[dict]:  成功した場合には一覧が入った list が返却されます
    """
    if not isinstance(page, int) and int(page) < 1:
        raise {"message": "ページの指定は1以上の整数値で行う必要があります"}

    headers = build_header()
    endpoint = "/api/v1/transcriptions"
    full_url = urljoin(MOCOVOICE_API_URL, endpoint)

    data = await api_call(
        lambda client: client.get(full_url, headers=headers, params={"page": page})
    )
    return extract_transcriptions(data)


@mcp.tool(name="SHOW_TRANSCRIPTION_RESULT")
async def show_transcription(transcription_id: str) -> dict[str, str]:
    """書き起こしを取得して表示します
    Args:
        transcription_id: str
            書き起こしID (UUID)

    Returns:
        dict[str, str]: 失敗した場合にはエラーメッセージが、成功した場合には書き起こしの結果が返却されます
    """

    if not is_valid_uuid(transcription_id):
        return {
            "message": "与えられた文字列は正しい書き起こしIDのフォーマットに従っていません"
        }
    headers = build_header()
    url = urljoin(MOCOVOICE_API_URL, f"/api/v1/transcriptions/{transcription_id}")
    data = await api_call(lambda client: client.get(url, headers=headers))
    status = data["status"]
    if status != "COMPLETED":
        return {
            "message": "指定された書き起こしは完了していません。書き起こしには5~10分かかります。しばらく時間を置いてから再度お試しください"
        }

    transcription_path = data["transcription_path"]
    data = await api_call(lambda client: client.get(transcription_path), timeout=3600)
    return data


def main() -> None:
    mcp.run(transport="stdio")
