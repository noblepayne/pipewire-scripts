#!/usr/bin/env python3

import os
import subprocess
from typing import List, Tuple

def list_flac_files() -> List[str]:
    return sorted(f for f in os.listdir('.') if (f.lower().endswith('.flac') or f.lower().endswith('*.wav') or f.lower().endswith('*.m4a') ) and os.path.isfile(f))

def get_duration(filename: str) -> float:
    """Returns duration in seconds."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0

def format_mmss(seconds: float) -> str:
    minutes = int(seconds) // 60
    sec = int(seconds) % 60
    return f"{minutes:02}:{sec:02}"

def format_hhmmss(seconds: float) -> str:
    total = int(seconds)
    hours = total // 3600
    minutes = (total % 3600) // 60
    sec = total % 60
    return f"{hours:02}:{minutes:02}:{sec:02}"

def main():
    files = list_flac_files()
    if not files:
        print("No .flac files found.")
        return

    durations: List[Tuple[str, float]] = [(f, get_duration(f)) for f in files]
    total = sum(d for _, d in durations)

    max_name_len = max(len(f) for f, _ in durations)
    print(f"{'File':<{max_name_len}} | Duration (MM:SS)")
    print("-" * (max_name_len + 21))

    for f, d in durations:
        print(f"{f:<{max_name_len}} | {format_mmss(d)}")

    print("-" * (max_name_len + 21))
    print(f"{'Total':<{max_name_len}} | {format_mmss(total)}")
    print(f"\nTotal duration: {total:.2f} seconds")
    print(f"HH:MM:SS      : {format_hhmmss(total)}")

if __name__ == '__main__':
    main()
