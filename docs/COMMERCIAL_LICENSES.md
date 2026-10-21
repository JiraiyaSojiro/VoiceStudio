# Commercial licenses

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

| Model | License | Commercial OK | Source |
| --- | --- | --- | --- |
| `FunAudioLLM/Fun-CosyVoice3-0.5B-2512` | apache-2.0 | Yes | https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 |
| `KittenML/kitten-tts-mini-0.8` | apache-2.0 | Yes | https://huggingface.co/KittenML/kitten-tts-mini-0.8 |
| `Matthijs/cmu-arctic-xvectors` | mit | Yes | https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors |
| `OpenMOSS-Team/MOSS-Audio-Tokenizer` | apache-2.0 | Yes | https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer |
| `OpenMOSS-Team/MOSS-TTS-Nano` | apache-2.0 | Yes | https://huggingface.co/OpenMOSS-Team/MOSS-TTS-Nano |
| `OpenMOSS-Team/MOSS-TTS-Nano-100M` | apache-2.0 | Yes | https://huggingface.co/OpenMOSS-Team/MOSS-TTS-Nano-100M |
| `OpenMOSS-Team/MOSS-TTS-v1.5` | apache-2.0 | Yes | https://huggingface.co/OpenMOSS-Team/MOSS-TTS-v1.5 |
| `Systran/faster-distil-whisper-large-v3` | mit | Yes | https://huggingface.co/Systran/faster-distil-whisper-large-v3 |
| `Systran/faster-whisper-base` | mit | Yes | https://huggingface.co/Systran/faster-whisper-base |
| `Systran/faster-whisper-large-v2` | mit | Yes | https://huggingface.co/Systran/faster-whisper-large-v2 |
| `Systran/faster-whisper-large-v3` | mit | Yes | https://huggingface.co/Systran/faster-whisper-large-v3 |
| `Systran/faster-whisper-medium` | mit | Yes | https://huggingface.co/Systran/faster-whisper-medium |
| `Systran/faster-whisper-small` | mit | Yes | https://huggingface.co/Systran/faster-whisper-small |
| `Systran/faster-whisper-tiny` | mit | Yes | https://huggingface.co/Systran/faster-whisper-tiny |
| `ThuraAung1601/speecht5_for_thai_tts_v1` | mit | Yes | https://huggingface.co/ThuraAung1601/speecht5_for_thai_tts_v1 |
| `UsefulSensors/moonshine-base` | mit | Yes | https://huggingface.co/UsefulSensors/moonshine-base |
| `UsefulSensors/moonshine-tiny` | mit | Yes | https://huggingface.co/UsefulSensors/moonshine-tiny |
| `csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8` | cc-by-4.0 | Yes | https://huggingface.co/csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8 |
| `csukuangfj/sherpa-onnx-streaming-paraformer-bilingual-zh-en` | apache-2.0 | Yes | https://huggingface.co/csukuangfj/sherpa-onnx-streaming-paraformer-bilingual-zh-en |
| `csukuangfj/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20` | apache-2.0 | Yes | https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20 |
| `csukuangfj/sherpa-onnx-streaming-zipformer-en-20M-2023-02-17` | apache-2.0 | Yes | https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-en-20M-2023-02-17 |
| `csukuangfj/sherpa-onnx-streaming-zipformer-zh-14M-2023-02-23` | apache-2.0 | Yes | https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-zh-14M-2023-02-23 |
| `deepdml/faster-whisper-large-v3-turbo-ct2` | mit | Yes | https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2 |
| `facebook/w2v-bert-2.0` | mit | Yes | https://huggingface.co/facebook/w2v-bert-2.0 |
| `funasr/campplus` | apache-2.0 | Yes | https://huggingface.co/funasr/campplus |
| `kyutai/pocket-tts` | cc-by-4.0 | Yes | https://huggingface.co/kyutai/pocket-tts |
| `lj1995/GPT-SoVITS` | mit | Yes | https://huggingface.co/lj1995/GPT-SoVITS |
| `microsoft/speecht5_hifigan` | mit | Yes | https://huggingface.co/microsoft/speecht5_hifigan |
| `mlx-community/Dia-1.6B` | apache-2.0 | Yes | https://huggingface.co/mlx-community/Dia-1.6B |
| `mlx-community/Kokoro-82M-bf16` | apache-2.0 | Yes | https://huggingface.co/mlx-community/Kokoro-82M-bf16 |
| `mlx-community/MeloTTS-English-v3-MLX` | mit | Yes | https://huggingface.co/mlx-community/MeloTTS-English-v3-MLX |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit` | apache-2.0 | Yes | https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit |
| `mlx-community/csm-1b-8bit` | apache-2.0 | Yes | https://huggingface.co/mlx-community/csm-1b-8bit |
| `mlx-community/parakeet-tdt-0.6b-v3` | cc-by-4.0 | Yes | https://huggingface.co/mlx-community/parakeet-tdt-0.6b-v3 |
| `mlx-community/whisper-large-v3-mlx` | mit | Yes | https://huggingface.co/mlx-community/whisper-large-v3-mlx |
| `netease-youdao/Confucius4-TTS` | apache-2.0 | Yes | https://huggingface.co/netease-youdao/Confucius4-TTS |
| `nvidia/bigvgan_v2_22khz_80band_256x` | mit | Yes | https://huggingface.co/nvidia/bigvgan_v2_22khz_80band_256x |
| `nvidia/parakeet-tdt-0.6b-v2` | cc-by-4.0 | Yes | https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2 |
| `nvidia/parakeet-tdt-0.6b-v3` | cc-by-4.0 | Yes | https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 |
| `openai/whisper-large-v3` | apache-2.0 | Yes | https://huggingface.co/openai/whisper-large-v3 |
| `openai/whisper-large-v3-turbo` | mit | Yes | https://huggingface.co/openai/whisper-large-v3-turbo |
| `openbmb/VoxCPM2` | apache-2.0 | Yes | https://huggingface.co/openbmb/VoxCPM2 |
| `pyannote/segmentation-3.0` | mit | Yes | https://huggingface.co/pyannote/segmentation-3.0 |
| `pyannote/speaker-diarization-3.1` | mit | Yes | https://huggingface.co/pyannote/speaker-diarization-3.1 |
| `pyannote/wespeaker-voxceleb-resnet34-LM` | cc-by-4.0 | Yes | https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM |
| `rednote-hilab/dots.tts-soar` | apache-2.0 | Yes | https://huggingface.co/rednote-hilab/dots.tts-soar |
| `IndexTeam/IndexTTS-2.5` | bilibili-model-license | Yes, with conditions | https://huggingface.co/IndexTeam/IndexTTS-2.5 |
| `Supertone/supertonic-3` | openrail | Yes, with conditions | https://huggingface.co/Supertone/supertonic-3 |
| `Serveurperso/OmniVoice-GGUF` | CC-BY-NC-4.0; Higgs Audio 2; Meta Llama 3 | No | https://huggingface.co/Serveurperso/OmniVoice-GGUF |
| `audio-cpp/audio.cpp-gguf` | other | No | https://huggingface.co/audio-cpp/audio.cpp-gguf |
| `csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8` | NOASSERTION | No | https://huggingface.co/csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8 |
| `csukuangfj/sherpa-onnx-whisper-tiny` | NOASSERTION | No | https://huggingface.co/csukuangfj/sherpa-onnx-whisper-tiny |
| `eustlb/higgs-audio-v2-tokenizer` | NOASSERTION | No | https://huggingface.co/eustlb/higgs-audio-v2-tokenizer |
| `facebook/nllb-200-distilled-600M` | CC-BY-NC-4.0 | No | https://huggingface.co/facebook/nllb-200-distilled-600M |
| `iic/SenseVoiceSmall` | NOASSERTION | No | https://modelscope.cn/models/iic/SenseVoiceSmall |
| `k2-fsa/OmniVoice` | CC-BY-NC (version unspecified); Higgs Audio 2; Meta Llama 3 | No | https://huggingface.co/k2-fsa/OmniVoice |
| `mlx-community/Chatterbox-TTS-4bit` | NOASSERTION | No | https://huggingface.co/mlx-community/Chatterbox-TTS-4bit |
| `mlx-community/Llama-OuteTTS-1.0-1B-4bit` | CC-BY-NC-SA-4.0 AND Llama-3.2 | No | https://huggingface.co/mlx-community/Llama-OuteTTS-1.0-1B-4bit |
| `mlx-community/whisper-large-v3-turbo` | NOASSERTION | No | https://huggingface.co/mlx-community/whisper-large-v3-turbo |
| `mlx-community/whisper-tiny-mlx` | NOASSERTION | No | https://huggingface.co/mlx-community/whisper-tiny-mlx |

## Audited overrides

These decisions win over the tag on the card.

| Model | License | Commercial OK | Source |
| --- | --- | --- | --- |
| `IndexTeam/IndexTTS-2.5` | bilibili-model-license | Yes, with conditions | https://huggingface.co/IndexTeam/IndexTTS-2.5 |
| `3scale/qwen-tts-thai-sft` | — | No | https://huggingface.co/3scale/qwen-tts-thai-sft |
| `Bird/F5-TTS-THAI` | — | No | https://huggingface.co/Bird/F5-TTS-THAI |
| `ChayapholSmile/F5-TTS-THAI` | — | No | https://huggingface.co/ChayapholSmile/F5-TTS-THAI |
| `VIZINTZOR/F5-TTS-THAI` | — | No | https://huggingface.co/VIZINTZOR/F5-TTS-THAI |
| `archcross/kaiko-tts-thai` | — | No | https://huggingface.co/archcross/kaiko-tts-thai |
| `facebook/mms-tts-tha` | — | No | https://huggingface.co/facebook/mms-tts-tha |
| `kunato/wayu-kokoro-thai-v1` | — | No | https://huggingface.co/kunato/wayu-kokoro-thai-v1 |
| `tranhuyluyen/piper-voices-thai` | — | No | https://huggingface.co/tranhuyluyen/piper-voices-thai |
| `wannaphong/OmniVoice` | — | No | https://huggingface.co/wannaphong/OmniVoice |

## Unresolved asset families

The app can also touch these families. None is cleared for ads.

- `OmniVoice text/audio tokenizer components` — license `NOASSERTION`, not cleared
- `audioseal_wm_16bits / audioseal_detector_16bits` — license `NOASSERTION`, not cleared
- `htdemucs` — license `NOASSERTION`, not cleared
- `WhisperX language-specific alignment models and silero VAD` — license `NOASSERTION`, not cleared
- `fsmn-vad / cam++` — license `NOASSERTION`, not cleared
- `Argos language-pair packages` — license `NOASSERTION`, not cleared
- `User-provided Sherpa ONNX / RVC voice models / GPT-SoVITS server / custom MLX and env-overridden repos` — license `NOASSERTION`, not cleared

Shop voiceovers: [VoxCPM2](engines/voxcpm2.md).
