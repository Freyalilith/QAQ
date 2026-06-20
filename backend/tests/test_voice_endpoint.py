"""/api/voice/asr + /api/voice/tts endpoint behavior (#4)."""

import base64
import io
import wave

from app.core.config import Settings, get_settings
from app.main import app
from app.services.voice_provider import tts_cache


def test_asr_endpoint_transcribes_audio(client):
    response = client.post(
        "/api/voice/asr",
        content=b"\x01" * 4096,
        headers={"content-type": "audio/webm"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["transcript"].strip()
    assert body["is_mock"] is True
    assert body["provider"] == "mock"


def test_asr_endpoint_blank_on_empty_audio(client):
    response = client.post("/api/voice/asr", content=b"")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["transcript"] == ""


def test_asr_endpoint_rejects_oversized_audio(client):
    app.dependency_overrides[get_settings] = lambda: Settings(max_voice_upload_bytes=16)
    try:
        response = client.post("/api/voice/asr", content=b"x" * 64)
        assert response.status_code == 413
    finally:
        app.dependency_overrides.clear()


def test_tts_endpoint_returns_playable_wav(client):
    tts_cache.clear()
    response = client.post("/api/voice/tts", json={"text": "今天天气不错"})
    assert response.status_code == 200
    body = response.json()
    assert body["cached"] is False
    assert body["is_mock"] is True
    audio = base64.b64decode(body["audio_base64"])
    with wave.open(io.BytesIO(audio), "rb") as wav:
        assert wav.getnframes() > 0


def test_tts_endpoint_caches_repeat_text(client):
    tts_cache.clear()
    first = client.post("/api/voice/tts", json={"text": "重播这一句"}).json()
    second = client.post("/api/voice/tts", json={"text": "重播这一句"}).json()
    assert first["cached"] is False
    assert second["cached"] is True
    # Replay serves identical audio without re-synthesizing.
    assert first["audio_base64"] == second["audio_base64"]


def test_tts_endpoint_rejects_blank_text(client):
    assert client.post("/api/voice/tts", json={"text": "   "}).status_code == 422
    assert client.post("/api/voice/tts", json={"text": ""}).status_code == 422


# --- live-provider failure handling (#23): degrade, never 500 ----------------


class _BoomASR:
    name = "xiaomimimo"

    def transcribe(self, audio, *, content_type=None):
        raise RuntimeError("upstream API error")


class _BoomTTS:
    name = "xiaomimimo"

    def synthesize(self, text, *, voice=None):
        raise RuntimeError("upstream API error")


def test_asr_provider_failure_returns_not_ok(client, monkeypatch):
    # A real-API exception must surface as ok=false (retry prompt), not a 500.
    monkeypatch.setattr(
        "app.api.routes.voice.get_asr_provider", lambda settings: _BoomASR()
    )
    response = client.post(
        "/api/voice/asr", content=b"\x01" * 4096, headers={"content-type": "audio/wav"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["transcript"] == ""
    assert body["is_mock"] is False


def test_tts_provider_failure_returns_502(client, monkeypatch):
    tts_cache.clear()
    monkeypatch.setattr(
        "app.api.routes.voice.get_tts_provider", lambda settings: _BoomTTS()
    )
    response = client.post("/api/voice/tts", json={"text": "真实失败兜底测试"})
    assert response.status_code == 502
