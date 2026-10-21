"""Commercial-safe mode: on by default, off for the rest of the suite."""
from __future__ import annotations

import subprocess
import sys

import pytest

from core.commercial_safe import (
    CommercialUseBlocked,
    assert_engine_weights,
    assert_repo_allowed,
    assess,
    enabled,
)


@pytest.fixture
def commercial_on(monkeypatch):
    monkeypatch.setenv("VOICESTUDIO_COMMERCIAL_SAFE", "1")


def test_enabled_defaults_on(monkeypatch):
    monkeypatch.delenv("VOICESTUDIO_COMMERCIAL_SAFE", raising=False)
    assert enabled() is True


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "FALSE"])
def test_enabled_off_values(monkeypatch, value):
    monkeypatch.setenv("VOICESTUDIO_COMMERCIAL_SAFE", value)
    assert enabled() is False


def test_blocks_noncommercial_and_unknown(commercial_on):
    for repo_id in (
        "k2-fsa/OmniVoice",
        "facebook/nllb-200-distilled-600M",
        "mlx-community/whisper-large-v3-turbo",
        "iic/SenseVoiceSmall",
        "archcross/kaiko-tts-thai",
        "VIZINTZOR/F5-TTS-THAI",
        "wannaphong/OmniVoice",
    ):
        decision = assess(repo_id)
        assert decision.allowed is False, repo_id
        assert decision.status == "blocked"
        with pytest.raises(CommercialUseBlocked):
            assert_repo_allowed(repo_id)


def test_allows_mit_apache_and_conditions(commercial_on):
    thai = assess("ThuraAung1601/speecht5_for_thai_tts_v1")
    assert thai.allowed is True and thai.status == "allow"
    assert assess("KittenML/kitten-tts-mini-0.8").status == "allow"
    assert assess("openbmb/VoxCPM2").status == "allow"
    assert assess("microsoft/speecht5_hifigan").status == "allow"
    assert assess("Supertone/supertonic-3").status == "conditions"
    index = assess("IndexTeam/IndexTTS-2.5")
    assert index.allowed is True and index.status == "conditions"
    assert_repo_allowed("ThuraAung1601/speecht5_for_thai_tts_v1")


def test_engine_gate_uses_the_selected_checkpoint(commercial_on):
    with pytest.raises(CommercialUseBlocked):
        assert_engine_weights("omnivoice")
    assert_engine_weights("speecht5-thai", "ThuraAung1601/speecht5_for_thai_tts_v1")
    assert_engine_weights("mlx-audio", "mlx-community/Kokoro-82M-bf16")
    with pytest.raises(CommercialUseBlocked):
        assert_engine_weights("mlx-audio", "mlx-community/Llama-OuteTTS-1.0-1B-4bit")


def test_default_tts_engine_follows_the_flag(monkeypatch):
    from core import prefs
    from services.tts_backend import active_backend_id

    prefs.delete("tts_backend")
    monkeypatch.delenv("OMNIVOICE_TTS_BACKEND", raising=False)
    monkeypatch.delenv("VOICESTUDIO_COMMERCIAL_SAFE", raising=False)
    assert active_backend_id() == "speecht5-thai"
    monkeypatch.setenv("VOICESTUDIO_COMMERCIAL_SAFE", "0")
    assert active_backend_id() == "omnivoice"


def test_safe_catalogue_hides_omnivoice_and_requires_thai(commercial_on):
    from api.routers.setup import models as setup_models

    setup_models._cache.clear()
    payload = setup_models.list_models()
    assert payload["commercial_safe"] is True
    by_id = {row["repo_id"]: row for row in payload["models"]}
    assert by_id["k2-fsa/OmniVoice"]["commercial_ok"] is False
    assert by_id["k2-fsa/OmniVoice"]["required"] is False
    thai = by_id["ThuraAung1601/speecht5_for_thai_tts_v1"]
    assert thai["commercial_ok"] is True
    assert thai["required"] is True
    recommendations = setup_models.recommendations()
    ids = [row["repo_id"] for row in recommendations["models"]]
    assert "k2-fsa/OmniVoice" not in ids
    assert ids[0] == "ThuraAung1601/speecht5_for_thai_tts_v1"


def test_license_audit_doc_matches_the_gate():
    result = subprocess.run(
        [sys.executable, "scripts/export_commercial_licenses.py", "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
