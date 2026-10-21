"""Assemble a Thai ad voiceover: one line per sentence, pauses, tempo, -14 LUFS.

Synthesis stays in :mod:`services.thai_tts` (MIT SpeechT5) or, when a
reference recording is passed, in the existing VoxCPM2 engine (Apache-2.0,
Thai, voice cloning). This module only joins audio and calls ffmpeg.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

TARGET_LUFS = -14.0
TARGET_TP = -1.5
TARGET_LRA = 11.0


class VoiceoverError(RuntimeError):
    pass


def read_script(path: Path) -> list[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if text and not text.startswith("#"):
            lines.append(text)
    if not lines:
        raise VoiceoverError(f"{path} has no speakable lines.")
    return lines


def join_lines(clips: list[np.ndarray], sample_rate: int, pause_s: float) -> np.ndarray:
    """Concatenate mono clips with ``pause_s`` seconds of silence between them."""
    if sample_rate <= 0:
        raise VoiceoverError("sample_rate must be positive")
    if pause_s < 0:
        raise VoiceoverError("pause must be zero or positive")
    gap = np.zeros(int(round(pause_s * sample_rate)), dtype=np.float32)
    pieces: list[np.ndarray] = []
    for index, clip in enumerate(clips):
        audio = np.asarray(clip, dtype=np.float32).reshape(-1)
        if audio.size == 0:
            raise VoiceoverError(f"Line {index + 1} produced no audio.")
        pieces.append(audio)
        if index != len(clips) - 1 and gap.size:
            pieces.append(gap)
    if not pieces:
        raise VoiceoverError("No audio to join.")
    return np.concatenate(pieces)


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    pcm = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    ints = (pcm * 32767.0).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(ints.tobytes())


def atempo_filter(speed: float) -> str | None:
    """ffmpeg ``atempo`` chain for a pitch-preserving speed change. 1.0 is identity."""
    if speed <= 0:
        raise VoiceoverError("speed must be positive")
    if abs(speed - 1.0) < 1e-3:
        return None
    # atempo accepts 0.5–2.0 per filter. Chain to stay inside that window.
    factors: list[float] = []
    remaining = speed
    while remaining > 2.0:
        factors.append(2.0)
        remaining /= 2.0
    while remaining < 0.5:
        factors.append(0.5)
        remaining /= 0.5
    factors.append(remaining)
    return ",".join(f"atempo={factor:.5f}" for factor in factors)


def _ffmpeg() -> str:
    binary = shutil.which("ffmpeg")
    if not binary:
        raise VoiceoverError(
            "ffmpeg is required for tempo and -14 LUFS normalization. "
            "Install it (apt install ffmpeg) or use the copy VoiceStudio downloads "
            "during first-run setup."
        )
    return binary


def _run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=False, capture_output=True, text=True)


def _wav_rate(path: Path) -> int:
    with wave.open(str(path), "rb") as handle:
        return handle.getframerate()


def apply_tempo(src: Path, dst: Path, speed: float) -> None:
    chain = atempo_filter(speed)
    if chain is None:
        if src != dst:
            dst.write_bytes(src.read_bytes())
        return
    # Pin the rate. Some ffmpeg builds otherwise pick a high default and
    # the voiceover stops being 16 kHz speech.
    result = _run_ffmpeg([
        _ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src), "-af", chain, "-ar", str(_wav_rate(src)), str(dst),
    ])
    if result.returncode != 0:
        raise VoiceoverError(result.stderr.strip() or "ffmpeg atempo failed")


def _loudnorm_measurement(path: Path) -> dict | None:
    analysis = (
        f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json"
    )
    result = _run_ffmpeg([
        _ffmpeg(), "-hide_banner", "-i", str(path), "-af", analysis, "-f", "null", "-",
    ])
    text = result.stderr
    start = text.rfind("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        measured = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    needed = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
    if any(key not in measured for key in needed):
        return None
    return measured


def loudnorm_to(src: Path, dst: Path) -> None:
    """Compress, limit, then loudnorm to about -14 LUFS.

    SpeechT5's peaks are tall relative to the average. Plain loudnorm stops
    at the true-peak ceiling and leaves a short line several LU quiet.
    The compressor brings the average up; the limiter keeps the peak in
    check; loudnorm finishes at the target. The source sample rate is kept.
    """
    analysis = (
        "acompressor=threshold=-30dB:ratio=8:attack=2:release=40:makeup=16,"
        "alimiter=limit=0.89,"
        f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}"
    )
    codec = ["-c:a", "aac", "-b:a", "192k"] if dst.suffix.lower() == ".m4a" else []
    result = _run_ffmpeg([
        _ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src), "-af", analysis, "-ar", str(_wav_rate(src)), *codec, str(dst),
    ])
    if result.returncode != 0:
        raise VoiceoverError(result.stderr.strip() or "ffmpeg loudnorm failed")


def render(
    lines: list[str],
    output: Path,
    *,
    voice: str = "slt",
    speed: float = 1.0,
    pause_s: float = 0.4,
    engine: str = "speecht5-thai",
    reference: Path | None = None,
    reference_text: str | None = None,
) -> Path:
    """Synthesize ``lines`` and write a WAV or M4A normalized to about -14 LUFS."""
    from core.commercial_safe import assert_engine_weights, assert_repo_allowed

    output = output.expanduser().resolve()
    if output.suffix.lower() not in {".wav", ".m4a"}:
        raise VoiceoverError("Output must be a .wav or .m4a file.")
    if engine == "voxcpm2":
        if reference is None:
            raise VoiceoverError(
                "VoxCPM2 voice cloning needs --ref pointing at your own 20–30 s WAV or M4A. "
                "For a preset Thai voice without a recording, omit --engine."
            )
        assert_repo_allowed("openbmb/VoxCPM2")
        clips, sample_rate = _voxcpm_lines(lines, reference, reference_text)
    elif engine in {"speecht5-thai", "speecht5"}:
        assert_engine_weights("speecht5-thai", "ThuraAung1601/speecht5_for_thai_tts_v1")
        if reference is not None:
            raise VoiceoverError(
                "SpeechT5 Thai cannot clone a recording. It uses a fixed MIT CMU Arctic "
                "timbre (see --voice). To clone your own voice, install VoxCPM2 and rerun "
                "with --engine voxcpm2 --ref your-voice.wav. VoxCPM2 is Apache-2.0, speaks "
                "Thai, and needs roughly 8 GB of free RAM. It is slow on CPU."
            )
        from services.thai_tts import synthesize

        clips = []
        sample_rate = None
        for line in lines:
            audio, sample_rate = synthesize(line, voice=voice)
            clips.append(audio)
        if sample_rate is None:
            raise VoiceoverError("No lines to speak.")
    else:
        raise VoiceoverError(
            f"Unknown engine {engine!r}. Use speecht5-thai (CPU preset) or voxcpm2 (clone)."
        )
    joined = join_lines(clips, sample_rate, pause_s)
    work = output.with_suffix(".raw.wav")
    paced = output.with_suffix(".paced.wav")
    write_wav(work, joined, sample_rate)
    try:
        apply_tempo(work, paced, speed)
        loudnorm_to(paced, output)
    finally:
        work.unlink(missing_ok=True)
        if paced != output:
            paced.unlink(missing_ok=True)
    return output


def _voxcpm_lines(lines, reference: Path, reference_text: str | None):
    import torch

    from services.tts_backend import VoxCPM2Backend
    from services.watermark import mark_synthetic

    ok, reason = VoxCPM2Backend.is_available()
    if not ok:
        raise VoiceoverError(reason)
    backend = VoxCPM2Backend()
    clips = []
    for line in lines:
        tensor = backend.generate(
            line,
            language="th",
            ref_audio=str(reference),
            ref_text=reference_text,
            speed=1.0,
        )
        if not isinstance(tensor, torch.Tensor):
            tensor = torch.as_tensor(tensor)
        tensor = mark_synthetic(tensor, backend.sample_rate, context="thai_voiceover.voxcpm2")
        clips.append(tensor.detach().float().cpu().numpy().reshape(-1))
    return clips, backend.sample_rate
