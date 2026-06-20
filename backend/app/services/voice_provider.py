"""ASR / TTS provider interfaces, selection, and a small TTS cache (issues #4, #23).

Voice I/O sits behind these interfaces so the demo runs fully offline in
``DEMO_MODE=true`` with deterministic mock providers (AGENTS.md §7) — no
microphone model and no paid speech API. Issue #4 ships the mock providers; #23
adds a real ASR/TTS provider behind the same contract, keeping the mock fallback
so a live-API outage never breaks the demo.

``transcribe`` never raises on empty/too-short audio — it returns an empty
transcript so the caller can show a gentle "I didn't catch that" prompt and keep
the text path working (FR-01 fallback).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, replace
from typing import Optional

from app.core.config import Settings

logger = logging.getLogger(__name__)

# Provider names that mean "use the offline mock" (kept in sync with config).
MOCK_PROVIDER_NAMES = {"mock", "fake"}
# Provider names that select the real xiaomimimo voice provider (#23).
XIAOMIMIMO_PROVIDER_NAMES = {"xiaomimimo", "mimo"}


@dataclass
class ASRResult:
    """Outcome of transcribing one audio clip.

    An empty ``transcript`` with ``confidence == 0`` signals "nothing
    recognized" — the caller shows a gentle retry prompt rather than an error.
    """

    transcript: str
    confidence: float
    provider: str = "mock"
    is_final: bool = True


@dataclass
class TTSResult:
    """Synthesized audio for one reply. ``cached`` is set by ``synthesize_cached``."""

    audio: bytes
    content_type: str
    provider: str = "mock"
    voice: str = ""
    cached: bool = False


class ASRProvider(ABC):
    name: str = "base"

    @abstractmethod
    def transcribe(
        self, audio: bytes, *, content_type: Optional[str] = None
    ) -> ASRResult:
        """Transcribe spoken audio to text. Must not raise on empty audio."""


class TTSProvider(ABC):
    name: str = "base"

    @abstractmethod
    def synthesize(self, text: str, *, voice: Optional[str] = None) -> TTSResult:
        """Synthesize speech audio for ``text``."""


def get_asr_provider(settings: Settings) -> ASRProvider:
    """Select an ASR provider.

    ``DEMO_MODE`` always uses the offline mock (so the demo never needs a key);
    only ``DEMO_MODE=false`` with a named real provider hits the live API (#23).
    """
    # Imported here to avoid a circular import at module load.
    from app.services.mock_voice_provider import MockASRProvider

    provider = (settings.asr_provider or "").strip().lower()
    if provider in MOCK_PROVIDER_NAMES:
        return MockASRProvider()
    if settings.demo_mode:
        logger.info(
            "DEMO_MODE=true: using the mock ASR provider regardless of "
            "ASR_PROVIDER=%r.",
            provider,
        )
        return MockASRProvider()
    if provider in XIAOMIMIMO_PROVIDER_NAMES:
        from app.services.xiaomimimo_voice_provider import XiaomiMiMoASRProvider

        if not settings.openai_api_key:
            raise RuntimeError(
                f"ASR_PROVIDER={provider!r} needs OPENAI_API_KEY (set it in .env)."
            )
        return XiaomiMiMoASRProvider(settings)
    raise RuntimeError(
        f"ASR provider {provider!r} is not available. Set ASR_PROVIDER to "
        "mock | xiaomimimo, or DEMO_MODE=true."
    )


def get_tts_provider(settings: Settings) -> TTSProvider:
    """Select a TTS provider (DEMO_MODE stays mock; see ``get_asr_provider``)."""
    from app.services.mock_voice_provider import MockTTSProvider

    provider = (settings.tts_provider or "").strip().lower()
    if provider in MOCK_PROVIDER_NAMES:
        return MockTTSProvider()
    if settings.demo_mode:
        logger.info(
            "DEMO_MODE=true: using the mock TTS provider regardless of "
            "TTS_PROVIDER=%r.",
            provider,
        )
        return MockTTSProvider()
    if provider in XIAOMIMIMO_PROVIDER_NAMES:
        from app.services.xiaomimimo_voice_provider import XiaomiMiMoTTSProvider

        if not settings.openai_api_key:
            raise RuntimeError(
                f"TTS_PROVIDER={provider!r} needs OPENAI_API_KEY (set it in .env)."
            )
        return XiaomiMiMoTTSProvider(settings)
    raise RuntimeError(
        f"TTS provider {provider!r} is not available. Set TTS_PROVIDER to "
        "mock | xiaomimimo, or DEMO_MODE=true."
    )


class _TTSCache:
    """Tiny in-memory LRU for synthesized replies.

    Provider-agnostic so the real provider (#23) reuses it — the point of the
    cache is to avoid re-synthesizing (and, for a paid provider, re-paying for)
    the same reply on replay. Process-local and bounded; fine for a single-user
    demo, not a durable store.
    """

    def __init__(self, max_entries: int = 64) -> None:
        self._store: "OrderedDict[tuple[str, str, str], TTSResult]" = OrderedDict()
        self._max = max_entries

    def get(self, key: tuple[str, str, str]) -> Optional[TTSResult]:
        result = self._store.get(key)
        if result is not None:
            self._store.move_to_end(key)
        return result

    def put(self, key: tuple[str, str, str], value: TTSResult) -> None:
        self._store[key] = value
        self._store.move_to_end(key)
        while len(self._store) > self._max:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()


# Process-wide cache shared across requests (tests call ``tts_cache.clear()``).
tts_cache = _TTSCache()


def synthesize_cached(
    provider: TTSProvider, text: str, *, voice: Optional[str] = None
) -> TTSResult:
    """Synthesize ``text``, returning a cached result on repeat (``cached=True``)."""
    key = (provider.name, voice or "", text)
    hit = tts_cache.get(key)
    if hit is not None:
        return replace(hit, cached=True)
    result = provider.synthesize(text, voice=voice)
    tts_cache.put(key, result)
    return result
