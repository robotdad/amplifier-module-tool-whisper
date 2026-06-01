---
bundle:
  name: whisper-transcriber
  version: 1.0.0
  description: Audio transcription assistant powered by OpenAI Whisper

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/robotdad/amplifier-module-tool-whisper@main
---

# Whisper Transcriber

A minimal bundle that adds audio transcription to an Amplifier session using the
OpenAI Whisper API.

## Quick Start

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. Run:
   ```bash
   amplifier run --bundle examples/whisper.md
   ```

3. Use in conversation:
   ```
   > Transcribe meeting-recording.mp3
   > Transcribe ~/downloads/podcast-episode.m4a in Spanish
   > Transcribe all MP3 files in the recordings/ directory
   ```

## What You Get

One tool is available in your session:

- **whisper** — Transcribe audio or video files to text using OpenAI Whisper.
  Saves `.transcript.txt` to `~/transcripts/` by default.

## Custom Configuration

Override defaults by adding a `tools:` section:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/robotdad/amplifier-module-tool-whisper@main

tools:
  - module: tool-whisper
    source: git+https://github.com/robotdad/amplifier-module-tool-whisper@main
    config:
      output_dir: ~/my-transcripts
      model: whisper-1
```

## File Size Limit

Whisper enforces a hard **25 MB** limit per file. For longer recordings, compress first:

```bash
ffmpeg -i long-recording.wav -b:a 64k output.mp3
```

## Combining with youtube-dl

When `youtube-dl` downloads a video but finds no YouTube transcript
(`transcript_available: false`), it returns `fallback_hint: no_transcript_use_whisper_on_video`
and a `path` field pointing to the saved file. The whisper tool accepts both `audio_path`
and `path`, so the handoff is direct — no copy or rename needed.

To use both tools together, compose all three bundles:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/robotdad/amplifier-youtube@main
  - bundle: git+https://github.com/robotdad/amplifier-module-tool-whisper@main
```

With both tools in session, the AI will:
1. Download the video and attempt to fetch a YouTube transcript
2. If no transcript is available, automatically pass the saved file to whisper

```
> Download and transcribe https://youtube.com/watch?v=...
> Download this podcast episode and transcribe it: https://...
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "OPENAI_API_KEY not set" | `export OPENAI_API_KEY="sk-..."` |
| "File too large" (>25 MB) | Compress: `ffmpeg -i input -b:a 64k output.mp3` |
| "File not found" | Use an absolute path or check the working directory |
| Inaccurate transcription | Pass a language hint in your request, e.g. "transcribe in French" |
