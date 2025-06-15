import json
import httpx
from contextlib import asynccontextmanager
from typing import Optional, Callable, Awaitable
from moco_voice_mcp.constant import ERROR_CODES


class APICallException(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


@asynccontextmanager
async def get_http_client(timeout: float = 10.0):
    async with httpx.AsyncClient(timeout=timeout) as client:
        yield client


async def api_call(
    func: Callable[[httpx.AsyncClient], Awaitable[httpx.Response]], timeout=10.0
):
    async with get_http_client(timeout=timeout) as client:
        try:
            response = await func(client)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if content_type == "application/json":
                return response.json()
            return {}
        except httpx.TimeoutException:
            raise APICallException(
                "リクエストがタイムアウトしました。しばらくしてから再度お試しください"
            )
        except httpx.HTTPStatusError as e:
            message = "リクエストに失敗しました。しばらくしてから再度お試しください"
            if e.response.status_code in ERROR_CODES.keys():
                message = ERROR_CODES[e.response.status_code]
            raise APICallException(message, status_code=e.response.status_code)
        except httpx.RequestError:
            raise APICallException(
                "ネットワークエラーが発生しました。しばらくしてから再度お試しください"
            )
        except json.JSONDecodeError:
            raise APICallException(
                "取得したデータのデコードに失敗しました。しばらくしてから再度お試しください"
            )
        except Exception:
            raise APICallException(
                "予期しないエラーが発生しました。しばらくしてから再度お試しください"
            )
