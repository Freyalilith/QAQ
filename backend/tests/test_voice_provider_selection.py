"""Provider selection: mock by name / in DEMO_MODE; real only when configured (#4, #23).

These tests never call the live API — they only assert which provider object is
selected. The real provider is constructed (not invoked) with a dummy key.
"""

import pytest

from app.core.config import Settings
from app.services.voice_provider import get_asr_provider, get_tts_provider


def test_mock_selected_when_named():
    assert get_asr_provider(Settings(asr_provider="mock")).name == "mock"
    assert get_tts_provider(Settings(tts_provider="mock")).name == "mock"


def test_demo_mode_uses_mock_even_with_real_provider_named():
    # DEMO_MODE must never need a key: a real provider name still yields mock.
    asr = get_asr_provider(
        Settings(asr_provider="xiaomimimo", demo_mode=True, openai_api_key="k")
    )
    tts = get_tts_provider(
        Settings(tts_provider="xiaomimimo", demo_mode=True, openai_api_key="k")
    )
    assert asr.name == "mock"
    assert tts.name == "mock"


def test_real_provider_selected_when_configured():
    asr = get_asr_provider(
        Settings(asr_provider="xiaomimimo", demo_mode=False, openai_api_key="k")
    )
    tts = get_tts_provider(
        Settings(tts_provider="xiaomimimo", demo_mode=False, openai_api_key="k")
    )
    assert asr.name == "xiaomimimo"
    assert tts.name == "xiaomimimo"


def test_real_provider_requires_api_key():
    with pytest.raises(RuntimeError):
        get_asr_provider(
            Settings(asr_provider="xiaomimimo", demo_mode=False, openai_api_key="")
        )
    with pytest.raises(RuntimeError):
        get_tts_provider(
            Settings(tts_provider="xiaomimimo", demo_mode=False, openai_api_key="")
        )


def test_unknown_provider_without_demo_mode_raises():
    with pytest.raises(RuntimeError):
        get_asr_provider(
            Settings(asr_provider="banana", demo_mode=False, openai_api_key="k")
        )
    with pytest.raises(RuntimeError):
        get_tts_provider(
            Settings(tts_provider="banana", demo_mode=False, openai_api_key="k")
        )
