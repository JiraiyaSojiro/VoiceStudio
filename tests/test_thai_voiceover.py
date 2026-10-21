"""Thai voiceover assembly. No model download."""
from __future__ import annotations

from pathlib import Path

import shutil
import wave

import numpy as np
import pytest

from services.thai_voiceover import (
    TARGET_LUFS,
    VoiceoverError,
    _loudnorm_measurement,
    atempo_filter,
    join_lines,
    loudnorm_to,
    read_script,
    render,
    write_wav,
)


def test_read_script_skips_blanks_and_comments(tmp_path: Path):
    script = tmp_path / "ad.txt"
    script.write_text("# note\n\nสวัสดีครับ\n  กระถางพิมพ์สามมิติ  \n", encoding="utf-8")
    assert read_script(script) == ["สวัสดีครับ", "กระถางพิมพ์สามมิติ"]


def test_read_script_rejects_an_empty_file(tmp_path: Path):
    script = tmp_path / "empty.txt"
    script.write_text("# only a comment\n\n", encoding="utf-8")
    with pytest.raises(VoiceoverError):
        read_script(script)


def test_join_lines_inserts_the_pause():
    clips = [np.ones(4, dtype=np.float32), np.full(2, 0.5, dtype=np.float32)]
    joined = join_lines(clips, 10, 0.3)
    assert joined.shape == (4 + 3 + 2,)
    assert joined[4] == 0
    assert joined[-1] == pytest.approx(0.5)


def test_join_lines_rejects_silence(tmp_path: Path):
    with pytest.raises(VoiceoverError):
        join_lines([np.zeros(0, dtype=np.float32)], 16000, 0.2)
    with pytest.raises(VoiceoverError):
        join_lines([np.ones(4, dtype=np.float32)], 16000, -0.1)


def test_atempo_chains_outside_the_ffmpeg_window():
    assert atempo_filter(1.0) is None
    assert atempo_filter(1.0004) is None
    assert atempo_filter(0.25) == "atempo=0.50000,atempo=0.50000"
    assert atempo_filter(3.0) == "atempo=2.00000,atempo=1.50000"


def test_speecht5_refuses_a_reference_clip(tmp_path: Path):
    with pytest.raises(VoiceoverError, match="cannot clone"):
        render(
            ["สวัสดี"],
            tmp_path / "out.wav",
            engine="speecht5-thai",
            reference=tmp_path / "voice.wav",
        )


def test_voxcpm_requires_a_reference(tmp_path: Path):
    with pytest.raises(VoiceoverError, match="--ref"):
        render(["สวัสดี"], tmp_path / "out.wav", engine="voxcpm2")


def test_loudnorm_keeps_the_rate_and_the_target(tmp_path: Path):
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg is not installed")
    rate = 16000
    t = np.arange(rate, dtype=np.float32) / rate
    write_wav(tmp_path / "quiet.wav", 0.02 * np.sin(2 * np.pi * 220 * t), rate)
    output = tmp_path / "norm.wav"
    loudnorm_to(tmp_path / "quiet.wav", output)
    with wave.open(str(output), "rb") as handle:
        assert handle.getframerate() == rate
    measured = _loudnorm_measurement(output)
    assert measured is not None
    assert abs(float(measured["input_i"]) - TARGET_LUFS) < 1.5


def test_output_must_be_wav_or_m4a(tmp_path: Path):
    with pytest.raises(VoiceoverError, match="wav"):
        render(["สวัสดี"], tmp_path / "out.mp3")
