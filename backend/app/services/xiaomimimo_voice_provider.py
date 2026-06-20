"""Real ASR / TTS via the xiaomimimo OpenAI-compatible API (issue #23).

xiaomimimo exposes voice through ``/chat/completions`` (omni-style), not the
OpenAI ``/audio/*`` paths:

* **TTS** (``mimo-v2.5-tts``): the text to speak goes in an *assistant* message
  with an ``audio.voice`` preset; the reply carries base64 WAV at
  ``choices[0].message.audio.data``.
* **ASR** (``mimo-v2.5-asr``): the clip goes in a user message as an
  ``input_audio`` part whose ``data`` is a **data URL** (``data:audio/wav;base64,
  …`` — bare base64 is rejected); the transcript comes back as
  ``choices[0].message.content``. The model accepts WAV / MP3.

These implement the same ``ASRProvider`` / ``TTSProvider`` contract as the mocks,
so they are selected only when ``DEMO_MODE=false`` and the provider is named;
``DEMO_MODE`` always stays on the offline mocks (AGENTS.md §7). The API key is
read from settings (gitignored ``.env``) and never logged.
"""

from __future__ import annotations

import base64
import logging
import time
from typing import Any, Optional

import httpx

from app.core.config import Settings
from app.services.voice_provider import ASRProvider, ASRResult, TTSProvider, TTSResult

logger = logging.getLogger(__name__)

_RETRY_ON = {429, 500, 502, 503, 504}


def _audio_format(content_type: Optional[str]) -> str:
    ct = (content_type or "").lower()
    if "mp3" in ct or "mpeg" in ct:
        return "mp3"
    return "wav"


class _XiaoMiMoClient:
    """Shared POST helper: auth, timeout, and one retry on rate-limit/5xx."""

    def __init__(self, settings: Settings) -> None:
        self._url = settings.openai_base_url.rstrip("/") + "/chat/completions"
        self._key = settings.openai_api_key
        self._timeout = settings.voice_provider_timeout_seconds

    def post(self, body: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }
        last_exc: Optional[Exception] = None
        for attempt in range(2):
            response = httpx.post(
                self._url, headers=headers, json=body, timeout=self._timeout
            )
            if response.status_code in _RETRY_ON and attempt == 0:
                logger.warning(
                    "xiaomimimo voice API %s; retrying once.", response.status_code
                )
                time.sleep(1.5)
                continue
            response.raise_for_status()
            return response.json()
        if last_exc:
            raise last_exc
        response.raise_for_status()
        return response.json()


class XiaomiMiMoASRProvider(ASRProvider):
    name = "xiaomimimo"

    def __init__(self, settings: Settings) -> None:
        self._client = _XiaoMiMoClient(settings)
        self._model = settings.asr_model

    def transcribe(
        self, audio: bytes, *, content_type: Optional[str] = None
    ) -> ASRResult:
        if not audio:
            return ASRResult(transcript="", confidence=0.0, provider=self.name)
        mime = (content_type or "audio/wav").split(";")[0]
        data_url = f"data:{mime};base64,{base64.b64encode(audio).decode('ascii')}"
        body = {
            "model": self._model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": data_url,
                                "format": _audio_format(content_type),
                            },
                        }
                    ],
                }
            ],
        }
        data = self._client.post(body)
        text = (data["choices"][0]["message"].get("content") or "").strip()
        return ASRResult(
            transcript=text,
            confidence=1.0 if text else 0.0,
            provider=self.name,
        )


class XiaomiMiMoTTSProvider(TTSProvider):
    name = "xiaomimimo"

    def __init__(self, settings: Settings) -> None:
        self._client = _XiaoMiMoClient(settings)
        self._model = settings.tts_model
        self._voice = settings.tts_voice

    def synthesize(self, text: str, *, voice: Optional[str] = None) -> TTSResult:
        chosen = voice or self._voice
        body = {
            "model": self._model,
            "messages": [{"role": "assistant", "content": text}],
            "audio": {"voice": chosen},
        }
        data = self._client.post(body)
        audio_b64 = data["choices"][0]["message"]["audio"]["data"]
        return TTSResult(
            audio=base64.b64decode(audio_b64),
            content_type="audio/wav",
            provider=self.name,
            voice=chosen,
        )
