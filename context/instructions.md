# Whisper Tool

You have access to the `whisper` transcription tool.

## whisper — Transcribe Audio

Convert audio files to text using the OpenAI Whisper API. Use this tool when you have a
local audio or video file and need its contents as text.

**When to use whisper:**
- You have a local audio or video file (`.mp3`, `.mp4`, `.wav`, `.m4a`, `.ogg`, `.flac`, etc.)
- After a `youtube-dl` download where `transcript_available` is `false` — use the `path` field
  from the download result directly as the input. The whisper tool accepts both `audio_path`
  and `path`, so the download→transcribe handoff is direct:
  - Download result contains `fallback_hint: no_transcript_use_whisper_on_video` and a `path` field
  - Pass that `path` value to the whisper tool

**When NOT to use whisper:**
- When `youtube-dl` already returned `transcript_available: true` — the transcript is already in
  `transcript.text`; there is nothing to transcribe
- For text documents, web URLs, or YouTube URLs — this tool only processes local audio/video files

**Parameters:**
- `audio_path` or `path` (required): Absolute or relative path to the audio or video file
- `language` (optional): Language hint for better accuracy, e.g. `"en"`, `"fr"`, `"es"`, `"de"`
  (default: auto-detect)

**Result fields:**
- `text`: Full transcript text
- `transcript_path`: Path to the saved `.transcript.txt` file
- `duration`: Audio duration in seconds
- `language`: Detected or specified language code
- `cost_usd`: Estimated API cost in USD (~$0.006/min)

**Important constraints:**
- **25 MB file size limit** — the tool validates before uploading and returns an error if exceeded.
  Advise the user to compress with ffmpeg if needed:
  `ffmpeg -i input.wav -b:a 64k output.mp3`
- **`OPENAI_API_KEY` must be set** — the tool uses the OpenAI hosted Whisper API. If the key is
  missing the tool returns a clean error; ask the user to set `export OPENAI_API_KEY="sk-..."`.
