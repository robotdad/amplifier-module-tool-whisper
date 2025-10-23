"""
Tests for WhisperTool
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from amplifier_module_tool_whisper import Transcript, TranscriptSegment, WhisperTool


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response."""
    response = MagicMock()
    response.text = "This is a test transcript."
    response.language = "en"
    response.duration = 10.5
    segment = MagicMock()
    segment.id = 0
    segment.start = 0.0
    segment.end = 10.5
    segment.text = "This is a test transcript."
    response.segments = [segment]
    return response


@pytest.fixture
def whisper_tool(tmp_path):
    """Create WhisperTool instance with temp output dir."""
    config = {"output_dir": str(tmp_path / "transcripts"), "model": "whisper-1"}
    return WhisperTool(config)


def test_whisper_tool_initialization(tmp_path):
    """Test WhisperTool initialization."""
    config = {"output_dir": str(tmp_path / "transcripts"), "model": "whisper-1", "api_key": "test-key"}

    with patch("amplifier_module_tool_whisper.core.OpenAI"):
        tool = WhisperTool(config)
        assert tool.name == "whisper"
        assert tool.description == "Transcribe audio using OpenAI Whisper API"
        assert tool.output_dir == tmp_path / "transcripts"
        assert tool.output_dir.exists()


def test_whisper_tool_default_config():
    """Test WhisperTool with default configuration."""
    with patch("amplifier_module_tool_whisper.core.OpenAI"):
        tool = WhisperTool()
        assert tool.output_dir == Path("~/transcripts").expanduser()


@pytest.mark.asyncio
async def test_execute_missing_audio_path(whisper_tool):
    """Test execute() with missing audio_path."""
    result = await whisper_tool.execute({})
    assert result.success is False
    assert result.error["type"] == "ValueError"
    assert "audio_path is required" in result.error["message"]


@pytest.mark.asyncio
async def test_execute_success(whisper_tool, mock_openai_response, tmp_path):
    """Test successful transcription."""
    audio_file = tmp_path / "test.mp3"
    audio_file.write_bytes(b"fake audio data")

    with patch.object(whisper_tool.transcriber, "transcribe") as mock_transcribe:
        transcript = Transcript(
            text="Test transcript",
            language="en",
            duration=10.5,
            segments=[TranscriptSegment(id=0, start=0.0, end=10.5, text="Test transcript")],
        )
        mock_transcribe.return_value = transcript

        result = await whisper_tool.execute({"audio_path": str(audio_file)})

        assert result.success is True
        assert result.output["text"] == "Test transcript"
        assert result.output["language"] == "en"
        assert result.output["duration"] == 10.5
        assert len(result.output["segments"]) == 1
        assert result.output["segments"][0]["text"] == "Test transcript"
        assert result.output["cost"] > 0


@pytest.mark.asyncio
async def test_execute_with_language_and_prompt(whisper_tool, tmp_path):
    """Test execute() with language and prompt options."""
    audio_file = tmp_path / "test.mp3"
    audio_file.write_bytes(b"fake audio data")

    with patch.object(whisper_tool.transcriber, "transcribe") as mock_transcribe:
        transcript = Transcript(text="Test", language="es", duration=5.0, segments=[])
        mock_transcribe.return_value = transcript

        result = await whisper_tool.execute(
            {"audio_path": str(audio_file), "language": "es", "prompt": "Meeting notes"}
        )

        mock_transcribe.assert_called_once()
        call_args = mock_transcribe.call_args
        assert call_args.kwargs["language"] == "es"
        assert call_args.kwargs["prompt"] == "Meeting notes"
        assert result.success is True


@pytest.mark.asyncio
async def test_execute_file_not_found(whisper_tool):
    """Test execute() with non-existent file."""
    result = await whisper_tool.execute({"audio_path": "/nonexistent/file.mp3"})

    assert result.success is False
    assert result.error["type"] == "ValueError"
    assert "not found" in result.error["message"]


@pytest.mark.asyncio
async def test_execute_transcription_error(whisper_tool, tmp_path):
    """Test execute() when transcription fails."""
    audio_file = tmp_path / "test.mp3"
    audio_file.write_bytes(b"fake audio data")

    with patch.object(whisper_tool.transcriber, "transcribe") as mock_transcribe:
        mock_transcribe.side_effect = ValueError("API error")

        result = await whisper_tool.execute({"audio_path": str(audio_file)})

        assert result.success is False
        assert result.error["type"] == "ValueError"
        assert "API error" in result.error["message"]


def test_cost_estimation():
    """Test cost estimation logic."""
    with patch("amplifier_module_tool_whisper.core.OpenAI"):
        tool = WhisperTool({"api_key": "test-key"})

        cost_1min = tool.transcriber.estimate_cost(60)
        assert abs(cost_1min - 0.006) < 0.0001

        cost_10min = tool.transcriber.estimate_cost(600)
        assert abs(cost_10min - 0.06) < 0.0001

        cost_half_min = tool.transcriber.estimate_cost(30)
        assert abs(cost_half_min - 0.003) < 0.0001


@pytest.mark.asyncio
async def test_execute_path_expansion(whisper_tool, tmp_path):
    """Test that ~ paths are expanded correctly."""
    with (
        patch.object(whisper_tool.transcriber, "transcribe") as mock_transcribe,
        patch("amplifier_module_tool_whisper.whisper_tool.Path.expanduser") as mock_expand,
    ):
        mock_expand.return_value = tmp_path / "test.mp3"
        (tmp_path / "test.mp3").write_bytes(b"fake")

        transcript = Transcript(text="Test", language="en", duration=5.0, segments=[])
        mock_transcribe.return_value = transcript

        await whisper_tool.execute({"audio_path": "~/test.mp3"})

        mock_expand.assert_called()


def test_file_size_validation(tmp_path):
    """Test that files larger than 25MB are rejected."""
    audio_file = tmp_path / "large.mp3"
    audio_file.write_bytes(b"x" * (26 * 1024 * 1024))

    with patch("amplifier_module_tool_whisper.core.OpenAI"):
        tool = WhisperTool({"api_key": "test-key"})

        with pytest.raises(ValueError, match="too large"):
            tool.transcriber.transcribe(audio_file)
