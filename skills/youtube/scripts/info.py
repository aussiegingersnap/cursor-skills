#!/usr/bin/env python3
"""Get YouTube video metadata."""

import argparse
import json
import subprocess
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "info"


def get_info(url: str, dump_json: bool = False, show_formats: bool = False) -> dict:
    """Fetch video metadata."""
    cmd = ["yt-dlp", "--dump-json", "--no-download", url]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    
    if dump_json:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUTPUT_DIR / f"{info['id']}.json"
        out.write_text(json.dumps(info, indent=2))
        print(f"Saved: {out}")
    
    return info


def format_duration(seconds: int) -> str:
    """Format seconds as HH:MM:SS."""
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main():
    parser = argparse.ArgumentParser(description="Get YouTube video info")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--json", "-j", action="store_true", help="Save full JSON")
    parser.add_argument("--formats", "-f", action="store_true", help="Show available formats")
    args = parser.parse_args()
    
    try:
        info = get_info(args.url, args.json, args.formats)
        
        print(f"\nTitle:    {info.get('title')}")
        print(f"Channel:  {info.get('channel')}")
        print(f"Duration: {format_duration(info.get('duration', 0))}")
        print(f"Views:    {info.get('view_count', 0):,}")
        print(f"Date:     {info.get('upload_date', 'N/A')}")
        print(f"ID:       {info.get('id')}")
        
        if args.formats:
            print("\nFormats:")
            for f in info.get("formats", [])[-10:]:
                res = f.get("resolution", "audio")
                ext = f.get("ext")
                note = f.get("format_note", "")
                print(f"  {f['format_id']:>6} | {res:>10} | {ext:>4} | {note}")
                
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        exit(1)


if __name__ == "__main__":
    main()
