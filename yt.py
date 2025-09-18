# import yt_dlp
from ytmusicapi import YTMusic
import os
import subprocess


ytm = YTMusic("browser.json")


def get_info(videoId: str) -> list:
    try:
        t = ytm.get_song(videoId)["videoDetails"]
        additional_info = ytm.get_watch_playlist(videoId)["tracks"][0]

        return [
            t.get("videoId", "unknown_id"),
            t.get("title", "Unknown"),
            ", ".join([a.get("name", "Unknown") for a in t.get("artists", [{"name": "Unknown"}])]),
            additional_info["album"]["name"],
            t.get("lengthSeconds", 0),
        ]
    except Exception as e:
        print(f"ytm get_song error: {e}")
        return []


def search(query: str) -> list[list]:
    try:
        tracks = ytm.search(query, filter="songs", limit=99)
        return [
            [
                t.get("videoId", "Unknown"),
                t.get("title", "Unknown"),
                ", ".join([a.get("name", "Unknown") for a in t.get("artists", [{"name": "Unknown"}])]),
                t.get("album", {"name": ["Unknown"]})["name"],
                t.get("duration_seconds", 0),
            ]
            for t in tracks
        ]
    except Exception as e:
        print(f"ytm search error: {e}")
        return []


def download(track: str, path: str) -> str:
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
        return path

    except Exception as e:
        print(f"yt-dlp error: {e}")
        return ""
