# SpeechT5 Thai

MIT Thai text-to-speech. A listen test of the preset voice found the Thai
unintelligible, so this fork does not select it by default. Commercial-safe
mode uses [VoxCPM2](voxcpm2.md) instead. Keep this engine only when you need
a small CPU download and can accept the quality.

The weights are [`ThuraAung1601/speecht5_for_thai_tts_v1`](https://huggingface.co/ThuraAung1601/speecht5_for_thai_tts_v1)
(MIT, fine-tune of `microsoft/speecht5_tts`). The vocoder is
[`microsoft/speecht5_hifigan`](https://huggingface.co/microsoft/speecht5_hifigan)
(MIT). The timbre is one CMU Arctic x-vector from
[`Matthijs/cmu-arctic-xvectors`](https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors)
(MIT). That is a preset speaker, not a clone of a recording you supply.

Training-data doubt: the fine-tune used `lunarlist/edited_common_voice`. The
dataset card says the voices come from Mozilla Common Voice (CC0) and were
modified so they would not sound like the original speakers. The card does
not name who modified them. The weight license is MIT. That is not a promise
about every hour of training audio.

## When to pick it

- Thai lines of a few seconds, on a machine with no GPU.
- Ads that must not use the non-commercial OmniVoice weights.

To clone your own 20–30 second recording, use [VoxCPM2](voxcpm2.md)
(`--engine voxcpm2 --ref clip.wav`). VoxCPM2 is Apache-2.0 and lists Thai.
It is a multi-gigabyte download and is slow on CPU. Plan on about 8 GB of
free RAM.

## CPU Linux

No NVIDIA/AMD GPU is required. Budget about 4 GB of free RAM for SpeechT5
and about 700 MB of disk for the weights, vocoder, and x-vectors.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers sentencepiece soundfile huggingface_hub numpy pyyaml
sudo apt install ffmpeg
```

Write `script.txt` with one Thai sentence per line. Blank lines and lines
that start with `#` are skipped.

```bash
PYTHONPATH=backend python scripts/thai_voiceover.py script.txt \
  -o ad.wav --voice slt --speed 1.0 --pause 0.4
```

`-o ad.m4a` writes AAC. The file stays at 16 kHz. Short lines are compressed and then loudness-normalized to about -14 LUFS, because the raw peaks would otherwise stop the gain early.
Voices: `slt` (default), `clb`, `bdl`, `rms`, `jmk`, `awb`, `ksp`.

Turn commercial-safe mode off only when you mean to use non-commercial
weights: `VOICESTUDIO_COMMERCIAL_SAFE=0`. The default in this fork is on.

## In the app

Select **SpeechT5 Thai** in the model catalogue, or export
`OMNIVOICE_TTS_BACKEND=speecht5-thai`. Output is 16 kHz mono. A reference
clip is refused; the error tells you to use VoxCPM2.
