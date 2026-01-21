#!/usr/bin/env python3
"""Download YouTube videos or extract audio."""

import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "output"


def download(url: str, audio_only: bool = False, quality: int = None, audio_format: str = "mp3"):
    """Download video or extract audio."""
    if audio_only:
        out_dir = BASE_DIR / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            "yt-dlp", "-x",
            "--audio-format", audio_format,
            "--audio-quality", "0",
            "-o", str(out_dir / "%(title)s.%(ext)s"),
            url
        ]
    else:
        out_dir = BASE_DIR / "videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]" if quality else "bestvideo+bestaudio/best"
        cmd = [
            "yt-dlp", "-f", fmt,
            "--merge-output-format", "mp4",
            "-o", str(out_dir / "%(title)s.%(ext)s"),
            url
        ]
    
    print(f"Downloading to: {out_dir}")
    subprocess.run(cmd, check=True)
    print("Done!")


def main():
    parser = argparse.ArgumentParser(description="Download YouTube video/audio")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--audio", "-a", action="store_true", help="Audio only")
    parser.add_argument("--quality", "-q", type=int, help="Max video height (e.g., 720)")
    parser.add_argument("--format", "-f", default="mp3", help="Audio format (mp3, m4a, opus)")
    args = parser.parse_args()
    
    try:
        download(args.url, args.audio, args.quality, args.format)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
