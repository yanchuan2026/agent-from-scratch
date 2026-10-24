"""LLM 客户端：统一处理超时、重试、错误和用量记录。"""

import logging
import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger(__name__)

API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT = 60.0
MAX_ATTEMPTS = 3
RETRY_BACKOFF_BASE = 0.5


class Usage(BaseModel):
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class ChatResult(BaseModel):
    content: str
    finish_reason: str | None = None
    model: str
    usage: Usage
    latency_ms: int = Field(ge=0)
    attempts: int = Field(ge=1)


class LLMError(Exception):
    """调用模型时的可预期错误。"""


class ConfigError(LLMError):
    """配置缺失，比如没有 API key。"""


def build_messages(system: str | None, user: str) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    return messages


def _extract(
    data: dict[str, Any], model: str, latency_ms: int, attempts: int
) -> ChatResult:
    choice = data["choices"][0]
    usage_raw = data.get("usage") or {}
    return ChatResult(
        content=choice["message"].get("content") or "",
        finish_reason=choice.get("finish_reason"),
        model=data.get("model", model),
        usage=Usage(
            prompt_tokens=usage_raw.get("prompt_tokens", 0),
            completion_tokens=usage_raw.get("completion_tokens", 0),
            total_tokens=usage_raw.get("total_tokens", 0),
        ),
        latency_ms=latency_ms,
        attempts=attempts,
    )


def chat(messages: list[dict[str, str]], **kwargs: Any) -> ChatResult:
    """调用模型；网络/超时/429/5xx 自动重试，其余错误立刻抛出。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ConfigError("没有找到 DEEPSEEK_API_KEY，检查项目根目录的 .env")

    model = kwargs.pop("model", DEFAULT_MODEL)
    timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": kwargs.pop("temperature", 0),
        "max_tokens": kwargs.pop("max_tokens", 1024),
    }
    payload.update(kwargs)

    headers = {"Authorization": f"Bearer {api_key}"}
    started = time.perf_counter()
    last_reason = "未知错误"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = httpx.post(
                API_URL, headers=headers, json=payload, timeout=timeout
            )
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_reason = f"{type(exc).__name__}: {exc}"
            logger.warning(
                "第 %d 次调用失败（网络/超时）：%s", attempt, last_reason
            )
        else:
            if response.status_code == 200:
                latency_ms = int((time.perf_counter() - started) * 1000)
                result = _extract(
                    response.json(), model, latency_ms, attempt
                )
                logger.info(
                    "调用成功 model=%s tokens=%d latency=%dms attempts=%d",
                    result.model,
                    result.usage.total_tokens,
                    result.latency_ms,
                    result.attempts,
                )
                return result

            if response.status_code == 429 or response.status_code >= 500:
                last_reason = (
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                logger.warning(
                    "第 %d 次调用失败（可重试）：%s", attempt, last_reason
                )
            else:
                raise LLMError(
                    f"请求失败 HTTP {response.status_code}: {response.text[:300]}"
                )

        if attempt < MAX_ATTEMPTS:
            delay = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            logger.info("%.1f 秒后重试", delay)
            time.sleep(delay)

    raise LLMError(f"重试 {MAX_ATTEMPTS} 次后仍失败：{last_reason}")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(message)s"
    )
    result = chat(
        build_messages(
            "你是一个简洁的助手，回答不超过三句话。",
            "用一句话说明什么是 AI Agent。",
        ),
        max_tokens=200,
    )
    print(result.content)
    print(result.model_dump())


if __name__ == "__main__":
    main()