#!/usr/bin/env python3
"""Extract transcripts from YouTube videos."""

import argparse
import re
import subprocess
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "transcripts"


def video_id(url: str) -> str:
    """Extract video ID from URL."""
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else url[:11]


def clean_vtt(content: str) -> str:
    """Parse VTT and return clean text."""
    lines, seen = [], set()
    for line in content.split("\n"):
        line = line.strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        if re.match(r"^\d+$|^\d{2}:\d{2}", line):
            continue
        line = re.sub(r"<[^>]+>|\{[^}]+\}", "", line)
        if line and line not in seen:
            seen.add(line)
            lines.append(line)
    return "\n".join(lines)


def extract(url: str, lang: str = "en", timestamps: bool = False) -> str:
    """Download subtitles and extract transcript."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    vid = video_id(url)
    
    # Download subtitles
    cmd = [
        "yt-dlp", "--write-sub", "--write-auto-sub",
        "--sub-lang", lang, "--sub-format", "vtt/srt/best",
        "--skip-download", "-o", str(OUTPUT_DIR / f"{vid}.%(ext)s"), url
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    
    # Find and parse subtitle file
    for f in OUTPUT_DIR.glob(f"{vid}*.vtt"):
        transcript = clean_vtt(f.read_text())
        f.unlink()  # Clean up
        
        # Save transcript
        out = OUTPUT_DIR / f"{vid}.txt"
        out.write_text(f"# {url}\n\n{transcript}")
        print(f"Saved: {out}")
        return transcript
    
    raise FileNotFoundError("No subtitles found")


def main():
    parser = argparse.ArgumentParser(description="Extract YouTube transcripts")
    parser.add_argument("url", help="YouTube URL or video ID")
    parser.add_argument("--lang", "-l", default="en")
    parser.add_argument("--timestamps", "-t", action="store_true")
    args = parser.parse_args()
    
    try:
        transcript = extract(args.url, args.lang, args.timestamps)
        print("\n" + transcript[:500] + "..." if len(transcript) > 500 else transcript)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
