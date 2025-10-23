"""
Whisper Tool - Amplifier Tool Protocol Wrapper

Wraps WhisperTranscriber in Amplifier Tool protocol for use in profiles.
"""

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

        Args:
            config: Optional configuration with keys:
                - output_dir: Directory to save transcripts (default: ~/transcripts)
                - model: Whisper model to use (default: whisper-1)
                - api_key: OpenAI API key (optional, can use env var)
        """
        config = config or {}
        self.output_dir = Path(config.get("output_dir", "~/transcripts")).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        model = config.get("model", "whisper-1")
        api_key = config.get("api_key")

        self.transcriber = WhisperTranscriber(api_key=api_key, model=model)

    @property
    def name(self) -> str:
        """Tool name for invocation."""
        return "whisper"

    @property
    def description(self) -> str:
        """Human-readable tool description."""
        return "Transcribe audio using OpenAI Whisper API"

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        """Execute Whisper transcription.

        Args:
            input: Input parameters:
                - audio_path (required): Path to audio file
                - language (optional): Language code (e.g., 'en')
                - prompt (optional): Prompt to guide transcription
                - max_retries (optional): Maximum retry attempts (default: 3)

        Returns:
            ToolResult with output containing:
                - text: Full transcript text
                - segments: List of timestamped segments
                - duration: Audio duration in seconds
                - language: Detected or specified language
                - cost: Estimated API cost in USD
        """
        try:
            audio_path = input.get("audio_path")
            if not audio_path:
                return ToolResult(success=False, error={"message": "audio_path is required", "type": "ValueError"})

            language = input.get("language")
            prompt = input.get("prompt")
            max_retries = input.get("max_retries", 3)

            audio_path = Path(audio_path).expanduser()
            logger.info(f"Starting transcription: {audio_path.name}")

            transcript = self.transcriber.transcribe(
                audio_path=audio_path, language=language, prompt=prompt, max_retries=max_retries
            )

            cost = 0.0
            if transcript.duration:
                cost = self.transcriber.estimate_cost(transcript.duration)

            output = {
                "text": transcript.text,
                "segments": [
                    {"id": seg.id, "start": seg.start, "end": seg.end, "text": seg.text} for seg in transcript.segments
                ],
                "duration": transcript.duration,
                "language": transcript.language,
                "cost": cost,
            }

            logger.info(f"Transcription successful: {len(transcript.text)} chars, ${cost:.4f}")
            return ToolResult(success=True, output=output)

        except ValueError as e:
            logger.error(f"Transcription failed: {e}")
            return ToolResult(success=False, error={"message": str(e), "type": "ValueError"})
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}", exc_info=True)
            return ToolResult(success=False, error={"message": str(e), "type": type(e).__name__})
