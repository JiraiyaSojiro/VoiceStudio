#!/usr/bin/env python3
"""Write docs/COMMERCIAL_LICENSES.md from the commercial-safe gate.

The table is the gate's decision for every registry model, with safe mode
forced on. Re-run this script when a model record or an audited override
changes. ``--check`` fails when the committed file drifted.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from core.commercial_safe import _AUDITED_BLOCK, _AUDITED_CONDITIONS, assess  # noqa: E402
from services.model_licenses import load_registry  # noqa: E402

_OUTPUT = ROOT / "docs" / "COMMERCIAL_LICENSES.md"

_INTRO = """# Commercial licenses

Audited 2026-10-21 for this fork. A license is not changed by forking.
`VOICESTUDIO_COMMERCIAL_SAFE` defaults to on. Set it to `0` to load
non-commercial weights such as OmniVoice.

The gate reads the license recorded from each model card
(`backend/config/model_licenses.json`) and a short list of audited
overrides where a permissive tag does not match the weights. `commercial_use`
in that file stays false until a reviewed clearance exists. This table uses
the license category, not that flag.

**Yes** means the weight license permits commercial use (MIT, Apache-2.0,
BSD, CC-BY, CC0, and the same family). **Yes, with conditions** means
commercial use is allowed with extra duties (OpenRAIL, CC-BY-SA, GPL-family,
Llama, or the bilibili IndexTTS cap). **No** means non-commercial terms, or
a missing / `NOASSERTION` / `other` license that this mode refuses.

This is not legal advice. Read the card before you publish an ad. Training
data can be less clear than the weight license. Those doubts are noted below
and are not treated as a new license.

## Thai ads

| Use | Model | Commercial OK | Notes |
| --- | --- | --- | --- |
| Default Thai voice, CPU | `openbmb/VoxCPM2` | Yes | Apache-2.0, and the card says the model is free for commercial use. Thai is one of the 30 languages. Plain text needs no reference clip; `--ref` clones a recording. The card says training used more than 2 million hours and does not list source-audio licenses. About 5 GB of weights and 8 GB of free RAM. Official PyTorch weights, not the Q8 GGUF. |
| Small MIT preset | `ThuraAung1601/speecht5_for_thai_tts_v1` | Yes | MIT on the card. A listen test found the Thai unintelligible, so it is not the default. Fine-tune of MIT `microsoft/speecht5_tts` on `lunarlist/edited_common_voice`. The dataset card says Common Voice (CC0) voices were modified so they would not sound like the originals, and does not name the modifier. |
| Default upstream voice | `k2-fsa/OmniVoice` | No | CC-BY-NC weights. Clips cannot be used in ads. |

Rejected Thai checkpoints that are not in the app catalog, checked the same day:

| Model | Why it is not commercial-OK |
| --- | --- |
| `wannaphong/OmniVoice` | Hugging Face tag is Apache-2.0. The weight blobs match `k2-fsa/OmniVoice` (same LFS object ids and sizes). A new tag does not change CC-BY-NC. |
| `archcross/kaiko-tts-thai`, `kunato/wayu-kokoro-thai-v1` | Apache-2.0 file tag. The Kokoro Thai line was trained on Som TTS audio synthesized by those OmniVoice weights. Not cleared. |
| `VIZINTZOR/F5-TTS-THAI`, `Bird/F5-TTS-THAI`, `ChayapholSmile/F5-TTS-THAI` | Cards say CC-BY-4.0. They are fine-tunes of `SWivid/F5-TTS` (CC-BY-NC-4.0). A fine-tune cannot drop the non-commercial term. |
| `facebook/mms-tts-tha`, `tranhuyluyen/piper-voices-thai` | CC-BY-NC-4.0. Piper has no official Thai voice; these files inherit MMS. |
| `3scale/qwen-tts-thai-sft` | Apache-2.0 tag. The card does not document the Thai fine-tune, and the config has no Thai language id. Not cleared. Too large for a small CPU machine. |
| `chuubjak/vits-tts-thai` | No license tag on the card. Not cleared. |
| `pythainlp/thaitts-onnx` | Apache-2.0 export of `lunarlist/tts-thai`. Same edited-Common-Voice line as SpeechT5. Whisper large-v3 character error on the shop script was about 88%. Not used. |
| `Qwen/Qwen3-TTS-12Hz-1.7B-Base` | Apache-2.0. The card lists 10 languages and Thai is not one of them. |
| `FunAudioLLM/Fun-CosyVoice3-0.5B-2512` | Apache-2.0. The card lists 9 languages and Thai is not one of them. |
| `OpenMOSS-Team/MOSS-TTS-Nano` | Apache-2.0, 20 languages, no Thai. |
| `VIZINTZOR/KaoPadTTS-85M` | No license on the card or the code repo. Not cleared. |
| `VIZINTZOR/VachanaTTS` | Card tag is MIT. An earlier project by the same author is a fine-tune of CC-BY-NC `facebook/mms-tts-tha`, and this card does not document the training audio. Not cleared. |
| `dubbing-ai/SiangTTS-VoxCPM2-Thai-LoRA` | CC-BY-SA-4.0. Commercial use is allowed with share-alike. Not the default, because the Apache-2.0 base already passed the intelligibility check. |

## Catalog

"""


def _cell(value: object) -> str:
    text = " ".join(str(value).split())
    return text.replace("|", "/")


def _label(status: str) -> str:
    if status == "allow":
        return "Yes"
    if status == "conditions":
        return "Yes, with conditions"
    return "No"


def _rows(repo_ids: list[str]) -> str:
    lines = [
        "| Model | License | Commercial OK | Source |",
        "| --- | --- | --- | --- |",
    ]
    decisions = [(repo_id, assess(repo_id)) for repo_id in repo_ids]
    decisions.sort(key=lambda item: (item[1].status != "allow", item[1].status != "conditions", item[0]))
    for repo_id, decision in decisions:
        license_name = decision.license_name or "—"
        lines.append(
            f"| `{_cell(repo_id)}` | {_cell(license_name)} | {_label(decision.status)} | {_cell(decision.source_url)} |"
        )
    return "\n".join(lines) + "\n"


def render() -> str:
    previous = os.environ.get("VOICESTUDIO_COMMERCIAL_SAFE")
    os.environ["VOICESTUDIO_COMMERCIAL_SAFE"] = "1"
    try:
        registry = load_registry()
        catalog = _rows([row["id"] for row in registry["models"]])
        overrides = _rows(sorted(set(_AUDITED_BLOCK) | set(_AUDITED_CONDITIONS)))
        assets = "\n".join(
            f"- `{item['id']}` — license `{item.get('license', 'NOASSERTION')}`, not cleared"
            for item in registry["dynamic_assets"]
        )
    finally:
        if previous is None:
            os.environ.pop("VOICESTUDIO_COMMERCIAL_SAFE", None)
        else:
            os.environ["VOICESTUDIO_COMMERCIAL_SAFE"] = previous
    return (
        _INTRO
        + catalog
        + "\n## Audited overrides\n\n"
        + "These decisions win over the tag on the card.\n\n"
        + overrides
        + "\n## Unresolved asset families\n\n"
        + "The app can also touch these families. None is cleared for ads.\n\n"
        + assets
        + "\n\nShop voiceovers: [VoxCPM2](engines/voxcpm2.md).\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.check:
        current = _OUTPUT.read_text(encoding="utf-8") if _OUTPUT.exists() else ""
        if current != content:
            print("docs/COMMERCIAL_LICENSES.md is stale; run scripts/export_commercial_licenses.py")
            return 1
        return 0
    _OUTPUT.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
