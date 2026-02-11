---
name: audio-transcription
description: >
  Transcribe audio files to text using AssemblyAI API. Use this skill whenever the user asks to
  transcribe audio, convert speech to text, get a transcript of a recording, or work with audio/video
  files that need text extraction. Trigger on phrases like "transcribe", "transcription",
  "speech to text", "расшифровка", "транскрибация", "транскрипция", or when the user uploads
  audio/video files (.mp3, .wav, .m4a, .flac, .ogg, .mp4, .webm) and wants text output.
  Also trigger when the user mentions AssemblyAI or wants timestamped text from audio.
---

# Audio Transcription with AssemblyAI

Transcribe audio/video files to text with paragraph-level timestamps using AssemblyAI.

## Requirements

- **API Key**: The environment variable `AAI_API_KEY` must be set. If not found, ask the user to provide it.
- **Python package**: `assemblyai` (install with `pip install assemblyai --break-system-packages`)

## Supported formats

Audio: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac`
Video: `.mp4`, `.webm`, `.mov`, `.avi`, `.mkv`

## Workflow

1. **Identify input files** — check `/mnt/user-data/uploads/` for uploaded audio/video files, or use paths provided by the user.
2. **Prepare API key** — ask user for the API key
3. **Install dependency** — `pip install assemblyai --break-system-packages` if not already installed.
4. **Run transcription** — execute the skill's `AAI_API_KEY={insert API key here} scripts/transcribe.py` with appropriate arguments.
5. **Deliver results** — copy output `.txt` files to `/mnt/user-data/outputs/` and present to user.

## Usage

```bash
# Single file
python scripts/transcribe.py --files /path/to/audio.mp3 --output /path/to/output/ --lang ru 

# Multiple files
python scripts/transcribe.py --files /path/to/a.mp3 /path/to/b.mp3 --output /path/to/output/ --lang en 

# All audio files in a directory
python scripts/transcribe.py --dir /path/to/audio_dir/ --output /path/to/output/ --lang ru
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--files` | One of `--files` or `--dir` | — | One or more audio/video file paths |
| `--dir` | One of `--files` or `--dir` | — | Directory to scan for audio/video files |
| `--output` | No | `./out` | Output directory for transcripts |
| `--lang` | No | `ru` | Language code (e.g., `ru`, `en`, `es`, `de`, `fr`, `zh`, `ja`) |
| `--speaker-labels` | No | `false` | Enable speaker diarization |

### Output format

Each input file produces a `.txt` file with timestamped paragraphs:

```
[00:00 - 00:15]:
First paragraph of transcribed text here.

[00:15 - 00:42]:
Second paragraph continues here.
```

If speaker labels are enabled:

```
[00:00 - 00:15] Speaker A:
First paragraph of transcribed text here.

[00:15 - 00:42] Speaker B:
Second paragraph continues here.
```

## Language codes

Common codes: `ru` (Russian), `en` (English), `es` (Spanish), `de` (German), `fr` (French), `zh` (Chinese), `ja` (Japanese), `ko` (Korean), `pt` (Portuguese), `it` (Italian).

Full list: https://www.assemblyai.com/docs/concepts/supported-languages

## Notes

- AssemblyAI uploads the file to their servers for processing. Large files may take a few minutes.
- The `universal` speech model is used by default — it supports all languages and provides best quality.
- If transcription fails for a file, the script logs the error and continues with remaining files.
