# import yt_dlp
from ytmusicapi import YTMusic
import os
import subprocess


ytm = YTMusic("browser.json")


def get_info(videoId: str) -> list[str]:
    t = ytm.get_song(videoId)
    return [
        t["videoId"],
        t["videoDetails"]["title"],
        ", ".join([a.get("name", "") for a in t.get("artists", [])]),
    ]


def search(query: str) -> list[list[str]]:
    tracks = ytm.search(query, filter="songs", limit=99)
    return [
        [
            t.get("videoId", ""),
            t.get("title", ""),
            ", ".join([a.get("name", "") for a in t.get("artists", [])]),
        ]
        for t in tracks
    ]


def download(track: str, path: str) -> bool:
    # Build the command
    cmd = [
        "yt-dlp",
        "--cookies",
        "cookies.txt",
        "--extract-audio",
        "--audio-format",
        "mp3",
        # '--audio-quality', f'{quality}K',
        "--embed-thumbnail",
        "--add-metadata",
        "--output",
        path,
        "--ignore-errors",
        "--no-overwrites",
        # '--verbose',  # Add verbose for debugging
        f"https://music.youtube.com/watch?v={track}",
    ]

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            check=True,  # Raise exception on non-zero exit code
        )
        return True

    except:
        return False
