"""
Amplifier Whisper Tool Module

Speech-to-text transcription using OpenAI's Whisper API.
"""

from .core import Transcript, TranscriptSegment, WhisperTranscriber
from .whisper_tool import WhisperTool

__all__ = ["WhisperTool", "Transcript", "TranscriptSegment", "WhisperTranscriber"]
