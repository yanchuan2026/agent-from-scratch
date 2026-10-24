import pytest

import agent.llm as llm


class FakeResponse:
    """假的 HTTP 响应，只带 llm.py 用到的那几个属性。"""

    def __init__(self, status: int, payload: dict | None = None, text: str = "") -> None:
        self.status_code = status
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict:
        return self._payload


OK_PAYLOAD = {
    "model": "deepseek-chat",
    "choices": [{"message": {"content": "测试回复"}, "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
}


@pytest.fixture(autouse=True)
def _setup(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(llm, "RETRY_BACKOFF_BASE", 0)   # 测试里不要真的等


def test_normal_call(monkeypatch) -> None:
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: FakeResponse(200, OK_PAYLOAD))

    result = llm.chat([{"role": "user", "content": "hi"}])

    assert result.content == "测试回复"
    assert result.finish_reason == "stop"
    assert result.usage.total_tokens == 30
    assert result.attempts == 1


def test_retries_on_429(monkeypatch) -> None:
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            return FakeResponse(429, text="rate limited")
        return FakeResponse(200, OK_PAYLOAD)

    monkeypatch.setattr(llm.httpx, "post", fake_post)

    result = llm.chat([{"role": "user", "content": "hi"}])

    assert result.attempts == 3
    assert calls["n"] == 3


def test_gives_up_after_three_server_errors(monkeypatch) -> None:
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        return FakeResponse(500, text="boom")

    monkeypatch.setattr(llm.httpx, "post", fake_post)

    with pytest.raises(llm.LLMError):
        llm.chat([{"role": "user", "content": "hi"}])

    assert calls["n"] == 3


def test_does_not_retry_on_401(monkeypatch) -> None:
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        return FakeResponse(401, text="unauthorized")

    monkeypatch.setattr(llm.httpx, "post", fake_post)

    with pytest.raises(llm.LLMError):
        llm.chat([{"role": "user", "content": "hi"}])

    assert calls["n"] == 1


def test_missing_api_key(monkeypatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(llm.ConfigError):
        llm.chat([{"role": "user", "content": "hi"}])