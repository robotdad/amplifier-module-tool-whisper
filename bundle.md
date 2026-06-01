---
bundle:
  name: whisper
  version: 1.0.0
  description: Audio transcription assistant — convert audio files to text using OpenAI Whisper

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: whisper:behaviors/whisper
---

# Whisper Transcription

@whisper:context/instructions.md

---

@foundation:context/shared/common-system-base.md
