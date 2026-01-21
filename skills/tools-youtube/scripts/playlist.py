#!/usr/bin/env python3
"""Handle YouTube playlists."""

import argparse
import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "output"


def list_videos(url: str) -> list:
    """Get all videos in playlist."""
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", url]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    videos = []
    for line in result.stdout.strip().split("\n"):
        if line:
            videos.append(json.loads(line))
    return videos


def download_playlist(url: str, audio_only: bool = False, quality: int = None, 
                      video_range: str = None, audio_format: str = "mp3"):
    """Download playlist videos."""
    if audio_only:
        out_dir = BASE_DIR / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            "yt-dlp", "-x",
            "--audio-format", audio_format,
            "-o", str(out_dir / "%(playlist_index)s - %(title)s.%(ext)s"),
        ]
    else:
        out_dir = BASE_DIR / "videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        fmt = f"bestvideo[height<={quality}]+bestaudio/best" if quality else "bestvideo+bestaudio/best"
        cmd = [
            "yt-dlp", "-f", fmt,
            "--merge-output-format", "mp4",
            "-o", str(out_dir / "%(playlist_index)s - %(title)s.%(ext)s"),
        ]
    
    if video_range:
        cmd.extend(["--playlist-items", video_range])
    
    cmd.append(url)
    print(f"Downloading to: {out_dir}")
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Handle YouTube playlists")
    parser.add_argument("url", help="Playlist URL")
    parser.add_argument("--download", "-d", action="store_true", help="Download videos")
    parser.add_argument("--audio", "-a", action="store_true", help="Audio only")
    parser.add_argument("--quality", "-q", type=int, help="Max video height")
    parser.add_argument("--range", "-r", help="Video range (e.g., 1-5, 1,3,5)")
    parser.add_argument("--format", "-f", default="mp3", help="Audio format")
    args = parser.parse_args()
    
    try:
        if args.download:
            download_playlist(args.url, args.audio, args.quality, args.range, args.format)
        else:
            videos = list_videos(args.url)
            print(f"\nPlaylist: {len(videos)} videos\n")
            for i, v in enumerate(videos, 1):
                title = v.get("title", "N/A")[:60]
                duration = v.get("duration")
                dur_str = f"{duration//60}:{duration%60:02d}" if duration else "?"
                print(f"{i:3}. [{dur_str:>6}] {title}")
                
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
