"""CPU Thai TTS on MIT weights.

``ThuraAung1601/speecht5_for_thai_tts_v1`` is a fine-tune of
``microsoft/speecht5_tts`` (MIT) on ``lunarlist/edited_common_voice``.
The vocoder is ``microsoft/speecht5_hifigan`` (MIT). The preset timbre is
one CMU Arctic x-vector from ``Matthijs/cmu-arctic-xvectors`` (MIT). That
is a fixed speaker, not a clone of a recording you supply.

Provenance doubt, stated on the dataset card: the Thai training voices were
taken from Mozilla Common Voice (CC0) and modified so they would not sound
like the original speakers. The card does not name the modifier.
"""
from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path

import numpy as np

logger = logging.getLogger("omnivoice.thai_tts")

REPO_ID = "ThuraAung1601/speecht5_for_thai_tts_v1"
VOCODER_REPO = "microsoft/speecht5_hifigan"
XVECTOR_REPO = "Matthijs/cmu-arctic-xvectors"
XVECTOR_REVISION = "5c1297a9eb6c91714ea77c0d4ac5aca9b6a952e5"
SAMPLE_RATE = 16000
DEFAULT_VOICE = "slt"
# Speaker codes packed in XVECTOR_REPO (MIT).
PRESET_VOICES = ("slt", "clb", "bdl", "rms", "jmk", "awb", "ksp")

_model = None
_processor = None
_vocoder = None


def _revision(repo_id: str) -> str:
    from services.hf_revisions import revision_for

    return revision_for(repo_id)


def _load():
    global _model, _processor, _vocoder
    if _model is not None:
        return
    import torch
    from transformers import SpeechT5ForTextToSpeech, SpeechT5HifiGan, SpeechT5Processor

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Loading SpeechT5 Thai on %s", device)
    _processor = SpeechT5Processor.from_pretrained(REPO_ID, revision=_revision(REPO_ID))
    _model = SpeechT5ForTextToSpeech.from_pretrained(REPO_ID, revision=_revision(REPO_ID))
    _model = _model.to(device)
    _vocoder = SpeechT5HifiGan.from_pretrained(VOCODER_REPO, revision=_revision(VOCODER_REPO))
    _vocoder = _vocoder.to(device)
    _model._voicestudio_device = device  # noqa: SLF001 — local handle, not a torch API


def speaker_embedding(voice: str = DEFAULT_VOICE) -> np.ndarray:
    """One 512-d x-vector for a CMU Arctic speaker code."""
    voice = (voice or DEFAULT_VOICE).strip().lower()
    if voice not in PRESET_VOICES:
        raise ValueError(
            f"Unknown SpeechT5 Thai voice {voice!r}. Choose one of: {', '.join(PRESET_VOICES)}."
        )
    from huggingface_hub import hf_hub_download

    zip_path = hf_hub_download(
        repo_id=XVECTOR_REPO,
        filename="spkrec-xvect.zip",
        repo_type="dataset",
        revision=XVECTOR_REVISION,
    )
    needle = f"_{voice}_"
    with zipfile.ZipFile(zip_path) as archive:
        names = sorted(
            name for name in archive.namelist()
            if name.endswith(".npy") and needle in Path(name).name
        )
        if not names:
            raise RuntimeError(
                f"No x-vector for voice {voice!r} in {XVECTOR_REPO} at {XVECTOR_REVISION}."
            )
        with archive.open(names[0]) as handle:
            vector = np.load(io.BytesIO(handle.read()))
    vector = np.asarray(vector, dtype=np.float32).reshape(-1)
    if vector.shape != (512,):
        raise RuntimeError(f"Expected a 512-d x-vector, got {vector.shape}.")
    return vector


def synthesize(text: str, voice: str = DEFAULT_VOICE, *, mark: bool = True) -> tuple[np.ndarray, int]:
    """Synthesize one Thai line. Returns float32 mono audio and the sample rate.

    The app's generate route also runs ``mark_synthetic``. This call does too
    so the standalone voiceover script marks audio when AudioSeal is installed.
    Marking is a no-op when it is off or the package is missing, and it never
    replaces a failed synthesis with silence.
    """
    import torch

    cleaned = " ".join((text or "").split())
    if not cleaned:
        raise ValueError("SpeechT5 Thai needs at least one word.")
    _load()
    device = _model._voicestudio_device  # noqa: SLF001
    embedding = torch.tensor(speaker_embedding(voice), device=device).unsqueeze(0)
    inputs = _processor(text=cleaned, return_tensors="pt")
    input_ids = inputs["input_ids"].to(device)
    with torch.inference_mode():
        wave = _model.generate_speech(input_ids, embedding, vocoder=_vocoder)
    audio = wave.detach().float().cpu().numpy().reshape(-1)
    if mark:
        try:
            from services.watermark import mark_synthetic

            marked = mark_synthetic(
                torch.from_numpy(audio).unsqueeze(0),
                SAMPLE_RATE,
                context="thai_tts.synthesize",
            )
            audio = marked.detach().float().cpu().numpy().reshape(-1)
        except Exception:  # noqa: BLE001 — marking must not discard speech
            logger.warning("SpeechT5 Thai watermark step skipped", exc_info=True)
    return np.asarray(audio, dtype=np.float32), SAMPLE_RATE
