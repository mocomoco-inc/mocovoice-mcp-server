import os
from pathlib import Path

MOCOVOICE_API_KEY: str = os.environ.get("MOCOVOICE_API_KEY", "")
MOCOVOICE_API_URL: str = os.environ.get("MOCOVOICE_API_URL", "")
ALLOWED_DIR = Path(os.environ.get("ALLOWED_DIR", "/workspace")).expanduser().resolve()
MAX_FILE_SIZE = 3 * 1024 * 1024 * 1024

# https://docs.mocomoco.ai/faq
SUPPORT_MEDIA_CONTENT_TYPES = {
    ".aac": "audio/aac",
    ".aiff": "audio/x-aiff",
    ".avi": "video/x-msvideo",
    ".caf": "audio/x-caf",
    ".flac": "audio/flac",
    ".flv": "video/x-flv",
    ".m4a": "audio/mp4",
    ".mov": "video/quicktime",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".ogg": "audio/ogg",
    ".rmvb": "application/vnd.rn-realmedia-vbr",
    ".wav": "audio/x-wav",
    ".wm": "video/x-ms-wm",
    ".wma": "audio/x-ms-wma",
}

ERROR_CODES = {
    400: "送信されたリクエストは不正です。送信内容を確認してください",
    401: "与えられたAPIキーにはアクセス権限がありません。APIキーが有効なものか確認してください。",
    403: "与えられたAPIキーには本操作を行う権限がありません。APIキーの権限が適切か確認してください。",
    404: "指定されたリソースが見つかりません。URLを確認してください。",
    405: "このリクエストメソッドは許可されていません。",
    408: "リクエストがタイムアウトしました。通信環境を確認してください。",
    429: "リクエストが多すぎます。しばらく待ってから再度お試しください。",
    500: "サーバーでエラーが発生しました。しばらくしてから再度お試しください。",
    501: "リクエストされた機能は実装されていません。",
    502: "ゲートウェイでエラーが発生しました。しばらくしてから再度お試しください。",
    503: "サービスが一時的に利用できません。しばらくしてから再度お試しください。",
    504: "ゲートウェイのタイムアウトが発生しました。通信環境を確認してください。",
}
