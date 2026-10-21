"""Commercial-safe mode for this fork.

``VOICESTUDIO_COMMERCIAL_SAFE`` defaults to on. Set it to ``0``, ``false``,
``no``, or ``off`` to load every catalog model, including non-commercial
weights such as OmniVoice.

A model is allowed when its declared license permits commercial use:

* permissive grants (MIT, Apache-2.0, BSD, CC-BY, CC0, ISC, Unlicense)
* grants that allow commercial use with extra duties (OpenRAIL, CC-BY-SA,
  GPL-family, Llama community licenses, and the audited bilibili IndexTTS
  agreement under its user and revenue caps)

Blocked:

* non-commercial terms (CC-BY-NC and registry statuses that say so)
* unknown, ``NOASSERTION``, or ``other``, unless an audited exception below
  names a license that permits commercial use
* weights whose permissive tag is a relabel or a fine-tune of a
  non-commercial model (the tag cannot erase the upstream grant)

``model_licenses.json`` ``commercial_use`` stays false until a reviewed
clearance exists. This gate reads the declared license category, not that
flag.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_OFF = {"0", "false", "no", "off"}
THAI_TTS_REPO = "ThuraAung1601/speecht5_for_thai_tts_v1"
VOXCPM_REPO = "openbmb/VoxCPM2"
_YAML = Path(__file__).resolve().parents[1] / "config" / "models.yaml"

# Re-uploads and fine-tunes that must not inherit a permissive tag.
_AUDITED_BLOCK: dict[str, str] = {
    "wannaphong/OmniVoice": (
        "The weight blobs match k2-fsa/OmniVoice (CC-BY-NC). An Apache-2.0 "
        "tag on a re-upload does not change that license."
    ),
    "archcross/kaiko-tts-thai": (
        "The file tag is Apache-2.0, but this Kokoro Thai fine-tune was "
        "trained on Som TTS audio synthesized by OmniVoice weights that are "
        "byte-identical to the CC-BY-NC checkpoint. Not cleared for ads."
    ),
    "kunato/wayu-kokoro-thai-v1": (
        "Apache-2.0 tag. The card does not identify training audio, and the "
        "related Kokoro Thai line was trained on OmniVoice-synthesized speech. "
        "Not cleared for ads."
    ),
    "VIZINTZOR/F5-TTS-THAI": (
        "The card says CC-BY-4.0, but the checkpoint is a fine-tune of "
        "SWivid/F5-TTS (CC-BY-NC-4.0). A fine-tune cannot drop the "
        "non-commercial term."
    ),
    "Bird/F5-TTS-THAI": (
        "Fine-tune of SWivid/F5-TTS (CC-BY-NC-4.0). The CC-BY-4.0 tag does "
        "not replace the base weight license."
    ),
    "ChayapholSmile/F5-TTS-THAI": (
        "Fine-tune of SWivid/F5-TTS (CC-BY-NC-4.0). The CC-BY-4.0 tag does "
        "not replace the base weight license."
    ),
    "tranhuyluyen/piper-voices-thai": (
        "CC-BY-NC-4.0. These Piper files are conversions of MMS-TTS Thai "
        "fine-tunes, and MMS-TTS is CC-BY-NC-4.0."
    ),
    "facebook/mms-tts-tha": "CC-BY-NC-4.0 on the model card. Non-commercial.",
    "3scale/qwen-tts-thai-sft": (
        "The tag is Apache-2.0, but the card does not document the Thai "
        "fine-tune data and the config has no Thai language id. Not cleared."
    ),
}

# Licenses the SPDX heuristic cannot read, checked against the model card.
_AUDITED_CONDITIONS: dict[str, str] = {
    "IndexTeam/IndexTTS-2.5": (
        "bilibili Model Use License permits commercial use below 100 million "
        "monthly active users and RMB 1 billion annual revenue. Thai is not "
        "a supported language."
    ),
}


class CommercialUseBlocked(RuntimeError):
    """Raised before a non-commercial or unverified model is installed or used."""

    def __init__(self, repo_id: str, reason: str, license_name: str | None = None):
        self.repo_id = repo_id
        self.reason = reason
        self.license_name = license_name
        super().__init__(
            f"Commercial-safe mode blocked {repo_id}: {reason} "
            "Set VOICESTUDIO_COMMERCIAL_SAFE=0 to allow non-commercial weights."
        )

    def detail(self) -> dict:
        return {
            "code": "commercial_use_blocked",
            "message": str(self),
            "repo_id": self.repo_id,
            "license": self.license_name,
        }


@dataclass(frozen=True)
class Decision:
    allowed: bool
    status: str  # off | allow | conditions | blocked
    license_name: str
    category: str
    reason: str
    source_url: str

    def as_dict(self) -> dict:
        return {
            "commercial_ok": self.allowed,
            "commercial_status": self.status,
            "commercial_license": self.license_name,
            "commercial_category": self.category,
            "commercial_reason": self.reason,
            "commercial_source_url": self.source_url,
        }


def enabled() -> bool:
    """True unless the operator turned commercial-safe mode off."""
    raw = os.environ.get("VOICESTUDIO_COMMERCIAL_SAFE", "1").strip().lower()
    return raw not in _OFF


@lru_cache(maxsize=1)
def _catalog_rows() -> tuple[dict, ...]:
    import yaml

    data = yaml.safe_load(_YAML.read_text(encoding="utf-8")) or {}
    rows = data.get("models") or []
    return tuple(row for row in rows if isinstance(row, dict))


def catalog_repos(engine_id: str) -> list[str]:
    return [
        row["repo_id"]
        for row in _catalog_rows()
        if engine_id in (row.get("engines") or [])
        and isinstance(row.get("repo_id"), str)
    ]


def assess(repo_id: str) -> Decision:
    """License decision for one repository. Safe mode off allows everything."""
    if not enabled():
        return Decision(True, "off", "", "", "Commercial-safe mode is off.", "")
    blocked = _AUDITED_BLOCK.get(repo_id)
    if blocked:
        return Decision(False, "blocked", "", "noncommercial", blocked, f"https://huggingface.co/{repo_id}")
    conditions = _AUDITED_CONDITIONS.get(repo_id)
    if conditions:
        return Decision(
            True, "conditions", "bilibili-model-license", "conditions", conditions,
            f"https://huggingface.co/{repo_id}",
        )
    from services.model_licenses import safe_disclosure

    info = safe_disclosure(repo_id)
    license_name = str(info.get("license") or "")
    category = str(info.get("license_category") or "unknown")
    source = str(info.get("source_url") or f"https://huggingface.co/{repo_id}")
    if category == "commercial":
        return Decision(
            True, "allow", license_name, category,
            f"{license_name or 'permissive license'} permits commercial use of the weights.",
            source,
        )
    if category == "conditions":
        return Decision(
            True, "conditions", license_name, category,
            f"{license_name or 'this license'} allows commercial use with extra conditions. "
            "Read the model card before you publish an ad.",
            source,
        )
    if category == "noncommercial":
        reason = (
            f"{license_name or 'This license'} does not allow commercial use. "
            "Clips made with these weights cannot be used in ads."
        )
    else:
        reason = (
            f"License is {license_name or 'not stated'} ({category}). "
            "Commercial-safe mode blocks a model until its card shows a "
            "license that permits commercial use."
        )
    return Decision(False, "blocked", license_name, category, reason, source)


def assert_repo_allowed(repo_id: str) -> Decision:
    decision = assess(repo_id)
    if not decision.allowed:
        raise CommercialUseBlocked(repo_id, decision.reason, decision.license_name or None)
    return decision


def assert_repos_allowed(repo_ids: list[str]) -> None:
    for repo_id in repo_ids:
        if repo_id:
            assert_repo_allowed(repo_id)


def assert_engine_weights(engine_id: str, identity: str | None = None) -> None:
    """Block a TTS engine when the checkpoint it would load is not allowed.

    Engines that pick one repo out of several (MLX-Audio) are judged on that
    repo. An engine with a single catalog repo is judged on that repo.
    """
    if not enabled():
        return
    repos: list[str] = []
    if isinstance(identity, str) and "/" in identity:
        repos.append(identity)
    rows = catalog_repos(engine_id)
    if len(rows) == 1:
        repos.append(rows[0])
    # Several checkpoints can share one engine id (MLX-Audio, Whisper).
    # Blocking every sibling because one of them is non-commercial would
    # also block a commercial checkpoint. The caller passes the checkpoint
    # it will load; install and the per-request licence hooks check that
    # repo on its own.
    assert_repos_allowed(list(dict.fromkeys(repos)))
