import yt_dlp
import ytmusicapi
import os
import asyncio
from queue import Queue


ytm = ytmusicapi.YTMusic()


async def get_info(videoId: str, info_msg):
    for i in range(3):
        try:
            return ytm.get_song(videoId)
        except:
            await info_msg.edit_text(f"Getting song info failed {i+1}/3")
            pass
    await info_msg.edit_text(f"Getting song info failed")
    return []


async def search(query: str, info_msg):
    for i in range(3):
        try:
            search_results = ytm.search(query, filter="songs", limit=99)
            await info_msg.delete()
            break
        except:
            await info_msg.edit_text(f"Search failed {i+1}/3")
            pass
    else:
        await info_msg.delete()
        search_results = []

    results = []
    i = 1
    for result in search_results:
        results.append(
            (
                f"{i} | {result.get("title", "Unknown")} | {result.get("artists", "Unknown")[0].get("name", "Unknown")} | {result.get("duration", "Unknown")}",
                result.get("videoId", "HUH???"),
            )
        )
        i += 1
    return results


async def download(track: str, info_msg):
    await update_progress(info_msg)
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
        for i in range(3):
            try:
                ydl.download(f"https://music.youtube.com/watch?v={track}")
                await info_msg.delete()
                return os.path.join("tracks", f"{track}.mp3")
            except:
                await info_msg.edit_text(f"Download failed {i+1}/3")
                pass
        return ""


progress_queue = Queue()


async def update_progress(info_msg):
    while True:
        text = progress_queue.get()
        if info_msg:
            await info_msg.edit_text(text)
        await asyncio.sleep(0.2)


def progress_hook(d):
    """Progress callback function"""
    if d["status"] == "downloading":
        progress_queue.put_nowait(f"Downloading: {str(d.get("_percent_str", "0%"))}")
    elif d["status"] == "finished":
        progress_queue.put_nowait(f"Downloaded, processing the output...")
