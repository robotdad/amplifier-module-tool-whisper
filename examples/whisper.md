---
profile:
  name: whisper-transcription
  extends: base

tools:
  - module: tool-whisper
    source: git+https://github.com/robotdad/amplifier-module-tool-whisper@main
    config:
      output_dir: ~/transcripts
      model: whisper-1
---

# Whisper Transcription Profile

Enables speech-to-text transcription using OpenAI Whisper in amplifier sessions.

## Quick Start

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

2. Activate this profile:
   ```bash
   amplifier run --profile whisper-transcription
   ```

3. Transcribe in conversation:
   ```
   > Transcribe meeting-recording.mp3
   ```

## What It Does

This profile adds the `tool-whisper` module to your amplifier session, enabling the AI to:

- Transcribe audio files to text
- Provide timestamped segments
- Estimate costs before processing
- Handle multiple languages automatically

## Configuration

The tool is configured to:
- Save transcripts to `~/transcripts/`
- Use Whisper's default `whisper-1` model
- Automatically handle retries on API failures

### Custom Configuration

Copy this profile to `~/.amplifier/profiles/my-transcribe.md` and adjust settings:

```yaml
tools:
  - module: tool-whisper
    source: git+https://github.com/robotdad/amplifier-module-tool-whisper@main
    config:
      output_dir: ~/my-custom-location
      model: whisper-1  # Currently only whisper-1 is available
```

## Example Workflows

### Transcribe a Single File

```
> Transcribe podcast-episode.mp3
```

The AI will:
1. Validate the audio file
2. Estimate the cost
3. Transcribe using Whisper
4. Save to ~/transcripts/

### Transcribe with Language Hint

```
> Transcribe french-audio.mp3 in French
```

The AI can pass language hints to improve accuracy for non-English audio.

### Batch Transcription

```
> Transcribe all MP3 files in the meetings/ directory
```

The AI will process multiple files sequentially, saving each transcript.

## Cost Awareness

Whisper API costs $0.006 per minute of audio. The tool provides cost estimates:

- 10-minute file: ~$0.06
- 60-minute podcast: ~$0.36
- 2-hour meeting: ~$0.72

## Troubleshooting

### "API key not found"

Set your OpenAI API key:
```bash
export OPENAI_API_KEY=sk-...
```

### "Audio file too large"

Whisper has a 25MB limit. Compress large files:
```bash
ffmpeg -i large-audio.wav -b:a 64k output.mp3
```

### "Transcription failed"

The tool automatically retries transient failures. If it fails after retries, check:
- API key is valid
- Audio file is accessible
- File format is supported (mp3, wav, m4a, etc.)

## Learn More

- [OpenAI Whisper Documentation](https://platform.openai.com/docs/guides/speech-to-text)
- [Amplifier Profiles Guide](https://github.com/microsoft/amplifier-dev/docs/profiles.md)
- [Tool Development](https://github.com/microsoft/amplifier-dev/docs/tool-development.md)
