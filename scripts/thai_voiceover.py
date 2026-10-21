#!/usr/bin/env python3
"""Thai product-ad voiceover from a text file. One line is one sentence.

Commercial-safe weights only. The default engine is MIT SpeechT5 Thai
(preset timbres, CPU). ``--engine voxcpm2 --ref clip.wav`` clones a 20–30 s
recording with Apache-2.0 VoxCPM2.

Example::

    python scripts/thai_voiceover.py script.txt -o ad.wav --voice slt --pause 0.4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from services.thai_tts import DEFAULT_VOICE, PRESET_VOICES  # noqa: E402
from services.thai_voiceover import VoiceoverError, read_script, render  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="UTF-8 text file, one Thai sentence per line")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output .wav or .m4a")
    parser.add_argument("--voice", default=DEFAULT_VOICE, choices=PRESET_VOICES)
    parser.add_argument("--speed", type=float, default=1.0, help="1.0 is unchanged. 1.1 is slightly faster.")
    parser.add_argument("--pause", type=float, default=0.4, help="Silence between lines, in seconds")
    parser.add_argument("--engine", default="speecht5-thai", choices=["speecht5-thai", "voxcpm2"])
    parser.add_argument("--ref", type=Path, default=None, help="Your own 20–30 s WAV or M4A. Requires voxcpm2.")
    parser.add_argument("--ref-text", default=None, help="Transcript of --ref, if you have one")
    args = parser.parse_args(argv)
    try:
        lines = read_script(args.script)
        output = render(
            lines,
            args.output,
            voice=args.voice,
            speed=args.speed,
            pause_s=args.pause,
            engine=args.engine,
            reference=args.ref,
            reference_text=args.ref_text,
        )
    except (VoiceoverError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
