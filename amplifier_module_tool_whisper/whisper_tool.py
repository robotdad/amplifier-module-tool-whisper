"""
Whisper Tool - Amplifier Tool Protocol Wrapper

Wraps WhisperTranscriber in Amplifier Tool protocol for use in profiles.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from amplifier_core.models import ToolResult

from .core import WhisperTranscriber

logger = logging.getLogger(__name__)


class WhisperTool:
    """OpenAI Whisper transcription tool."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize Whisper tool.

        The transcriber is constructed lazily on first execute() so that
        module load succeeds even when OPENAI_API_KEY is not set.

        Args:
            config: Optional configuration with keys:
                - output_dir: Directory to save transcripts (default: ~/transcripts)
                - model: Whisper model to use (default: whisper-1)
                - api_key: OpenAI API key (optional, can use env var)
        """
        config = config or {}
        self.output_dir = Path(config.get("output_dir", "~/transcripts")).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._model = config.get("model", "whisper-1")
        self._api_key = config.get("api_key")
        self._transcriber: WhisperTranscriber | None = None  # Lazily constructed

    def _get_transcriber(self) -> WhisperTranscriber | None:
        """Lazily construct the WhisperTranscriber.

        Returns None (rather than raising) when the OpenAI API key is absent,
        allowing execute() to surface a clean ToolResult error instead of a
        module-load crash.
        """
        if self._transcriber is None:
            try:
                self._transcriber = WhisperTranscriber(api_key=self._api_key, model=self._model)
            except ValueError:
                return None
        return self._transcriber

    @property
    def transcriber(self) -> WhisperTranscriber | None:
        """Return the underlying transcriber instance (None if not yet built)."""
        return self._transcriber

    @property
    def name(self) -> str:
        """Tool name for invocation."""
        return "whisper"

    @property
    def description(self) -> str:
        """Human-readable tool description."""
        return "Transcribe audio using OpenAI Whisper API"

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON schema describing the tool's input parameters."""
        return {
            "type": "object",
            "properties": {
                "audio_path": {
                    "type": "string",
                    "description": (
                        "Path to the audio file to transcribe "
                        "(alias: 'path' — accepts the 'path' key emitted by youtube-dl)."
                    ),
                },
                "path": {
                    "type": "string",
                    "description": "Alias for audio_path (the key emitted by youtube-dl).",
                },
                "language": {
                    "type": "string",
                    "description": "Optional ISO 639-1 language code (e.g., 'en') to guide transcription.",
                },
                "prompt": {
                    "type": "string",
                    "description": "Optional prompt to guide transcription style or vocabulary.",
                },
                "max_retries": {
                    "type": "integer",
                    "description": "Maximum retry attempts on transient failures (default: 3).",
                },
            },
            "required": [],
        }

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        """Execute Whisper transcription.

        Args:
            input: Input parameters:
                - audio_path (required): Path to audio file
                  (alias: path — accepts the 'path' key emitted by youtube-dl)
                - language (optional): Language code (e.g., 'en')
                - prompt (optional): Prompt to guide transcription
                - max_retries (optional): Maximum retry attempts (default: 3)

        Returns:
            ToolResult with output containing:
                - text: Full transcript text
                - transcript_path: Path to the saved .transcript.txt file
                - segments: List of timestamped segments
                - duration: Audio duration in seconds
                - language: Detected or specified language
                - cost_usd: Estimated API cost in USD
        """
        try:
            audio_path = input.get("audio_path") or input.get("path")
            if not audio_path:
                return ToolResult(
                    success=False, error={"message": "audio_path or path is required", "type": "ValueError"}
                )

            transcriber = self._get_transcriber()
            if transcriber is None:
                return ToolResult(
                    success=False,
                    error={
                        "message": "OpenAI API key required. Set OPENAI_API_KEY environment variable.",
                        "type": "ValueError",
                    },
                )

            language = input.get("language")
            prompt = input.get("prompt")
            max_retries = input.get("max_retries", 3)

            audio_path = Path(audio_path).expanduser()
            logger.info(f"Starting transcription: {audio_path.name}")

            transcript = await asyncio.to_thread(
                transcriber.transcribe,
                audio_path=audio_path,
                language=language,
                prompt=prompt,
                max_retries=max_retries,
            )

            cost_usd = 0.0
            if transcript.duration:
                cost_usd = transcriber.estimate_cost(transcript.duration)

            # Persist the transcript next to the configured output_dir so callers
            # (and the youtube-dl -> whisper handoff) get a stable file path back.
            transcript_path = self.output_dir / f"{audio_path.stem}.transcript.txt"
            transcript_path.write_text(transcript.text, encoding="utf-8")

            output = {
                "text": transcript.text,
                "transcript_path": str(transcript_path),
                "segments": [
                    {"id": seg.id, "start": seg.start, "end": seg.end, "text": seg.text} for seg in transcript.segments
                ],
                "duration": transcript.duration,
                "language": transcript.language,
                "cost_usd": cost_usd,
            }

            logger.info(f"Transcription successful: {len(transcript.text)} chars, ${cost_usd:.4f} -> {transcript_path}")
            return ToolResult(success=True, output=output)

        except ValueError as e:
            logger.error(f"Transcription failed: {e}")
            return ToolResult(success=False, error={"message": str(e), "type": "ValueError"})
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}", exc_info=True)
            return ToolResult(success=False, error={"message": str(e), "type": type(e).__name__})
