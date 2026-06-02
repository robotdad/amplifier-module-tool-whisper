# Amplifier Whisper Module

Transcription tool for Amplifier — convert audio files to text using the OpenAI Whisper API.

## Tool

### whisper — Transcribe Audio

- **Speech-to-text** — Transcribe audio or video files to plain text
- **Multi-language** — Supports 99+ languages; auto-detects language by default
- **Timestamped output** — Saves `.transcript.txt` to the configured output directory
- **youtube-dl handoff** — Accepts `audio_path` or `path` (the `path` key returned by
  `youtube-dl` when `transcript_available: false`)

**Parameters:**
- `audio_path` or `path` (required): Path to the audio or video file to transcribe
- `language` (optional): Language code to hint detection, e.g. `"en"`, `"fr"`, `"es"` (default: auto-detect)

**Result fields:**
- `text`: Full transcript text
- `transcript_path`: Path to the saved `.transcript.txt` file
- `duration`: Audio duration in seconds
- `language`: Detected or specified language code
- `cost_usd`: Estimated API cost in USD

## Prerequisites

- **Python 3.11+**
- **[UV](https://github.com/astral-sh/uv)** — Fast Python package manager
- **OpenAI API key** — Set as `OPENAI_API_KEY` (see [Configuration](#configuration))
- **amplifier-core** — Provided by the Amplifier runtime (not a declared package dependency)

### Installing UV

```bash
# macOS/Linux/WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

```bash
uv pip install -e .
```

## Usage

### As an Amplifier Bundle (ad-hoc use)

```bash
amplifier run --bundle git+https://github.com/robotdad/amplifier-module-tool-whisper@main \
  "Transcribe meeting-recording.mp3"
```

### Adding to Your Own Bundle

Include the `whisper` behavior in your bundle to add the transcription tool:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/robotdad/amplifier-module-tool-whisper@main
```

See [`examples/whisper.md`](examples/whisper.md) for a ready-to-run example bundle, including
the download→transcribe pattern when combining with `amplifier-youtube`.

### Custom Configuration

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

## Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `output_dir` | `~/transcripts` | Directory where `.transcript.txt` files are saved |
| `model` | `whisper-1` | Whisper model (currently only `whisper-1` is available) |
| `api_key` | — | OpenAI API key. Falls back to the `OPENAI_API_KEY` env var if not set in config. |

**Where to put the key.** The key is resolved in this order: (1) `api_key` in your bundle/module
config, then (2) the `OPENAI_API_KEY` environment variable. **Prefer the env var** so the secret
never lands in a committed YAML file:

```bash
export OPENAI_API_KEY="sk-..."   # in your shell profile, .env, or secret manager
```

## File Size Limit

The OpenAI Whisper API enforces a hard **25 MB** limit per file. The tool validates file size
before uploading and returns an error if the limit is exceeded.

For longer recordings or high-bitrate formats, compress with ffmpeg before transcribing:

```bash
ffmpeg -i input.wav -b:a 64k output.mp3
```

At 64 kbps, one hour of audio is approximately 28 MB — use 48 kbps if that is still over the
limit. Voice-only audio remains intelligible at these bitrates.

## Cost

Whisper API pricing is **~$0.006 per minute** of audio. The tool reports `cost_usd` in every result.

| File length | Approximate cost |
|-------------|-----------------|
| 10 minutes  | ~$0.06          |
| 1 hour      | ~$0.36          |
| 2 hours     | ~$0.72          |

For current pricing, see [OpenAI's pricing page](https://openai.com/pricing).

## Dependencies

- `openai>=1.0.0` — OpenAI API client

> **Note:** `amplifier-core` is a peer dependency provided by the Amplifier runtime — it is not
> listed as a Python package dependency of this module.

## Contributing

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
