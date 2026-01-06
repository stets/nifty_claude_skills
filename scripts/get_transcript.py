#!/usr/bin/env python3
"""
Extract transcript from a YouTube video.

Usage:
    python get_transcript.py <youtube_url_or_id> [--lang <language_code>] [--output <file>]

Examples:
    python get_transcript.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
    python get_transcript.py dQw4w9WgXcQ --lang en
    python get_transcript.py https://youtu.be/dQw4w9WgXcQ --output transcript.txt
"""

import argparse
import re
import sys
import json

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter, JSONFormatter
except ImportError:
    print("Error: youtube-transcript-api not installed.")
    print("Install with: pip install youtube-transcript-api")
    sys.exit(1)


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from various YouTube URL formats or return as-is if already an ID."""
    patterns = [
        r'(?:v=)([0-9A-Za-z_-]{11})',           # youtube.com/watch?v=ID
        r'(?:embed/)([0-9A-Za-z_-]{11})',        # youtube.com/embed/ID
        r'(?:youtu\.be/)([0-9A-Za-z_-]{11})',    # youtu.be/ID
        r'(?:shorts/)([0-9A-Za-z_-]{11})',       # youtube.com/shorts/ID
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # Check if it's already a valid video ID (11 chars, alphanumeric + _ -)
    if re.match(r'^[0-9A-Za-z_-]{11}$', url_or_id):
        return url_or_id

    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def get_transcript(video_id: str, languages: list[str] = None) -> tuple[list, dict]:
    """
    Fetch transcript for a YouTube video.

    Returns:
        tuple: (transcript_entries, metadata)
            - transcript_entries: List of {text, start, duration} dicts
            - metadata: Dict with video_id, language, is_generated
    """
    api = YouTubeTranscriptApi()

    if languages:
        transcript = api.fetch(video_id, languages=languages)
    else:
        transcript = api.fetch(video_id)

    entries = [{"text": e.text, "start": e.start, "duration": e.duration} for e in transcript]
    metadata = {
        "video_id": video_id,
        "language": transcript.language,
        "language_code": transcript.language_code,
        "is_generated": transcript.is_generated,
    }

    return entries, metadata


def format_as_text(entries: list) -> str:
    """Convert transcript entries to plain text."""
    return " ".join(entry["text"] for entry in entries)


def format_as_timestamped(entries: list) -> str:
    """Convert transcript entries to timestamped format."""
    lines = []
    for entry in entries:
        minutes = int(entry["start"] // 60)
        seconds = int(entry["start"] % 60)
        lines.append(f"[{minutes:02d}:{seconds:02d}] {entry['text']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extract transcript from a YouTube video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("url", help="YouTube URL or video ID")
    parser.add_argument("--lang", "-l", default=None,
                       help="Preferred language code (e.g., 'en', 'es', 'fr')")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--format", "-f", choices=["text", "timestamped", "json"],
                       default="text", help="Output format (default: text)")

    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
        languages = [args.lang] if args.lang else None

        entries, metadata = get_transcript(video_id, languages)

        # Format output
        if args.format == "json":
            output = json.dumps({"metadata": metadata, "transcript": entries}, indent=2)
        elif args.format == "timestamped":
            output = format_as_timestamped(entries)
        else:
            output = format_as_text(entries)

        # Write output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Transcript saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
