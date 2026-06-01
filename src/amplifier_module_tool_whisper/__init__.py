"""
Amplifier Whisper Tool Module

Speech-to-text transcription using OpenAI's Whisper API.
"""

import logging
from typing import Any

from .core import Transcript, TranscriptSegment, WhisperTranscriber
from .whisper_tool import WhisperTool

logger = logging.getLogger(__name__)

__all__ = ["WhisperTool", "Transcript", "TranscriptSegment", "WhisperTranscriber", "mount"]


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> None:
    """Mount the Whisper transcription tool into the coordinator.

    Follows the canonical amplifier-youtube mount() pattern:
    construct the tool, register it via coordinator.mount("tools", tool, name=tool.name),
    return None (no cleanup callable needed).
    """
    tool = WhisperTool(config or {})
    await coordinator.mount("tools", tool, name=tool.name)
    logger.info("whisper module mounted: whisper")
