#!/usr/bin/env python3
"""
Audio/video transcription using AssemblyAI.
Outputs timestamped paragraph text files.
"""

import argparse
from gettext import find
import os
import sys
from pathlib import Path


try:
    import assemblyai as aai
except ImportError:
    print("ERROR: assemblyai package not installed. Run: pip install assemblyai python-dotenv --break-system-packages")
    sys.exit(1)

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi", ".mkv"}
SUPPORTED_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS


def format_timestamp(milliseconds: int) -> str:
    """Convert milliseconds to MM:SS or HH:MM:SS format."""
    total_seconds = int(milliseconds / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def make_paragraphs(transcript, speaker_labels: bool = False) -> str:
    """Format transcript paragraphs with timestamps."""
    text_with_timecode = ""
    paragraphs = transcript.get_paragraphs()

    for paragraph in paragraphs:
        start_time = format_timestamp(paragraph.start)
        end_time = format_timestamp(paragraph.end)

        if speaker_labels and hasattr(paragraph, "speaker") and paragraph.speaker:
            text_with_timecode += f"[{start_time} - {end_time}] Speaker {paragraph.speaker}:\n{paragraph.text}\n\n"
        else:
            text_with_timecode += f"[{start_time} - {end_time}]:\n{paragraph.text}\n\n"

    return text_with_timecode.rstrip() + "\n"


def transcribe_file(
    transcriber: aai.Transcriber,
    audio_file: str,
    output_dir: str,
    speaker_labels: bool = False,
) -> bool:
    """Transcribe a single file. Returns True on success."""
    file_path = Path(audio_file)
    print(f"  Transcribing: {file_path.name} ...", flush=True)

    try:
        transcript = transcriber.transcribe(str(audio_file))

        if transcript.status == "error":
            print(f"  ERROR: Transcription failed for {file_path.name}: {transcript.error}")
            return False

        text = make_paragraphs(transcript, speaker_labels)
        output_file = Path(output_dir) / f"{file_path.stem}.txt"
        output_file.write_text(text, encoding="utf-8")
        print(f"  Done: {output_file}")
        return True

    except Exception as e:
        print(f"  ERROR: {file_path.name}: {e}")
        return False


def find_audio_files(directory: str) -> list[str]:
    """Find all supported audio/video files in a directory."""
    files = []
    for f in sorted(Path(directory).iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(str(f))
    return files


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio/video files using AssemblyAI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--files", nargs="+", help="Audio/video file paths to transcribe")
    group.add_argument("--dir", help="Directory containing audio/video files")
    parser.add_argument("--output", default="./out", help="Output directory (default: ./out)")
    parser.add_argument("--lang", default="ru", help="Language code (default: ru)")
    parser.add_argument("--speaker-labels", action="store_true", help="Enable speaker diarization")

    args = parser.parse_args()

    # Check API key
    api_key = os.environ.get("AAI_API_KEY")
    if not api_key:
        print("ERROR: AAI_API_KEY environment variable not set.")
        sys.exit(1)

    aai.settings.api_key = api_key

    # Collect files
    if args.dir:
        files = find_audio_files(args.dir)
        if not files:
            print(f"No supported audio/video files found in {args.dir}")
            sys.exit(1)
        print(f"Found {len(files)} file(s) in {args.dir}")
    else:
        files = args.files
        # Validate files exist
        for f in files:
            if not Path(f).exists():
                print(f"ERROR: File not found: {f}")
                sys.exit(1)

    # Create output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)

    # Configure transcriber
    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.universal,
        language_code=args.lang,
        punctuate=True,
        speaker_labels=args.speaker_labels,
    )
    transcriber = aai.Transcriber(config=config)

    # Transcribe
    print(f"\nTranscribing {len(files)} file(s) [lang={args.lang}]")
    print(f"Output directory: {args.output}\n")

    success = 0
    failed = 0
    for file in files:
        if transcribe_file(transcriber, file, args.output, args.speaker_labels):
            success += 1
        else:
            failed += 1

    print(f"\nResults: {success} succeeded, {failed} failed out of {len(files)} total")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
