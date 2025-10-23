# Amplifier Whisper Tool Module

Speech-to-text transcription using OpenAI's Whisper API.

## Features

- **Accurate transcription** - Powered by OpenAI Whisper API
- **Timestamped segments** - Get precise timing for each segment
- **Multiple languages** - Supports 99+ languages via Whisper
- **Cost estimation** - Know the API cost before transcribing
- **Automatic retry** - Handles transient API failures

## Prerequisites

- **Python 3.11+**
- **[UV](https://github.com/astral-sh/uv)** - Fast Python package manager
- **OpenAI API key** - Set as `OPENAI_API_KEY` environment variable

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

### As an Amplifier Tool

```python
from amplifier_module_tool_whisper import WhisperTool

# Create tool with config
tool = WhisperTool({
    "output_dir": "~/transcripts",
    "model": "whisper-1"
})

# Transcribe audio
result = await tool.execute({
    "audio_path": "audio.mp3",
    "language": "en"  # Optional
})

# Result includes:
# - text: Full transcript
# - segments: Timestamped segments
# - duration: Audio duration in seconds
# - language: Detected/specified language
# - cost: API cost in USD
```

### In an Amplifier Profile

Create `~/.amplifier/profiles/transcribe.md`:

```yaml
---
profile:
  name: transcribe
  extends: base

tools:
  - module: tool-whisper
    source: git+https://github.com/robotdad/amplifier-module-tool-whisper@main
    config:
      output_dir: ~/transcripts
---

# Transcription Profile

Enables speech-to-text transcription in amplifier sessions.
```

Then use in conversation:

```bash
amplifier run --profile transcribe
> "Transcribe audio.mp3"
```

## Configuration

Tool configuration options:

- `output_dir`: Where to save transcripts (default: `~/transcripts`)
- `model`: Whisper model to use (default: `whisper-1`)

## API Limits

OpenAI Whisper API has a 25MB file size limit. The tool validates file size before submitting.

If your audio exceeds 25MB, compress it first:

```bash
ffmpeg -i input.wav -b:a 64k -ar 16000 output.mp3
```

For current pricing information, check [OpenAI's pricing page](https://openai.com/pricing).

## Event Emission

Emits standard amplifier events:

- `tool:pre` - Before transcription starts
- `tool:post` - After successful transcription
- `tool:error` - On transcription failure

## Dependencies

- `openai>=1.0.0` - OpenAI API client
- `amplifier-core` - Core amplifier functionality

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
