import yt_dlp
import json
import os
import asyncio
from queue import Queue
import ytmusicapi


def search_youtube(query):
    try:
        ytm = ytmusicapi.YTMusic()
        return ytm.search(query, filter="songs", limit=99)
    except Exception as e:
        print(f"Error searching: {e}")
        return e


def search(text: str):
    search_results = search_youtube(text)
    if type(search_results) == Exception:
        return search_results
    results = []
    i = 1
    for result in search_results:
        results.append(
            (
                f"{i} | {result.get('title', 'Unknown')} | {result.get('artists', 'Unknown')[0].get("name", "Unknown")} | {result.get('duration', 'Unknown')}",
                result.get("videoId", "HUH???"),
            )
        )
        i += 1
    return results


def download(track: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join("tracks", f"{track}"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                # 'preferredquality': str(quality),
            },
            {
                "key": "FFmpegMetadata",
            },
            {
                "key": "EmbedThumbnail",
            },
        ],
        "writethumbnail": True,
        "addmetadata": True,
        "ignoreerrors": True,
        "nooverwrites": True,
        "quiet": False,
        "progress_hooks": [progress_hook],
        # 'cookiesfrombrowser': ('firefox',),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(f"https://music.youtube.com/watch?v={track}")

    return os.path.join("tracks", f"{track}.mp3")


progress_queue = Queue()


def progress_hook(d):
    """Progress callback function"""
    if d["status"] == "downloading":
        progress_queue.put_nowait(f"Downloading: {str(d.get('_percent_str', '0%'))}")
    elif d["status"] == "finished":
        progress_queue.put_nowait(f"Downloaded, processing the output...")


async def update_progress(msg):
    while True:
        text = progress_queue.get()
        if msg:
            await msg.edit_text(text)
        await asyncio.sleep(0.2)
